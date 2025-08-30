import asyncio
import functools
import time
from typing import Callable, TypeVar, Any, Optional, Union

from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.exception import DatabaseException, InvalidFieldException

T = TypeVar("T")


def transactional(
    func: Optional[Callable[..., T]] = None,
    *,
    readonly: bool = False,
    root: bool = False,
    session_attr: Optional[str] = None,
    isolation: str | None = None,
    readonly_tx: bool = False,
    timeout: int | None = None,
    retries: int = 0,
    savepoint: bool = False,
    auto_flush: bool = True,
    log_level: str | None = None,
    tag: str | None = None,
    expire_on_end: bool | None = None,
    auditable: bool = False,
    raise_on_empty: bool = False,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """
    Decorator that transparently manages SQLAlchemy **async** transactions.

    The decorator adapts to three common scenarios:

    • **Service layer** (`root=True`) – wraps the whole function
      in a single ``async with session.begin()`` so that multiple repository
      calls share one commit/rollback.

    • **Repository, stand‑alone** – opens an implicit transaction and commits
      (write) or commits‑to‑close (read) at the end of the method.

    • **Repository inside a service transaction** – flushes only; the service
      layer decides the final commit/rollback.

    -----
    Optional extras let you tune isolation level, add timeouts or automatic
    retries, create SAVEPOINTs, emit audit hooks, control object expiration
    and set per‑call logging.

    :param func: The function to decorate. If *None*, the decorator
    :param readonly: Logical hint — *True* if the method is read‑only.
    :param root: Wrap the function in a single transaction context manager.
    :param session_attr: Attribute name (``self.<attr>``) that contains the
                         repository holding the :class:`~sqlalchemy.ext.asyncio.AsyncSession`
                         when ``root=True``.
    :param isolation: Per‑call isolation level, e.g. ``"SERIALIZABLE"``.
    :param readonly_tx: Issue ``SET TRANSACTION READ ONLY`` for the session.
    :param timeout: Abort the coroutine if it exceeds *n* seconds.
    :param retries: Number of automatic retries on serialization or deadlock
                    errors (detected via ``OperationalError``).
    :param savepoint: Create a SAVEPOINT (``session.begin_nested()``) when an
                      outer transaction is already active.
    :param auto_flush: Disable if you do **not** want the decorator to call
                       :pymeth:`~sqlalchemy.ext.asyncio.AsyncSession.flush`
                       when it didn’t start the transaction.
    :param log_level: ``"DEBUG"``, ``"INFO"`` or *None* (silent).  Controls
                      what prints are emitted in the wrapper.
    :param tag: Arbitrary label appended to the log prefix (e.g. request‑id).
    :param expire_on_end: *True* → ``session.expire_all()`` after success;
                          *False* → guarantee objects stay valid; *None* →
                          inherit session default.
    :param auditable: If *True* and the decorator commits, an audit hook
                      (placeholder print) is triggered.
    :param raise_on_empty: Raise :class:`DatabaseException` when the wrapped
                           function returns *None*.
    :return: A callable that preserves the original function’s signature while
             adding transaction handling.
    :raises DatabaseException: Wrapped SQLAlchemy or domain errors.
    """

    # ───────────────────────── decorator factory ──────────────────────────
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        async def wrapper(self, *args: Any, **kwargs: Any) -> T:
            def _log(msg: str, lvl: str = "DEBUG") -> None:
                if log_level == "DEBUG" or (log_level == "INFO" and lvl != "DEBUG"):
                    print(msg)

            if root:
                if not session_attr:
                    raise ValueError("`session_attr` must be provided when root=True")
                repo = getattr(self, session_attr)
                session: AsyncSession = getattr(repo, "session", None)
            else:
                session: AsyncSession = getattr(self, "session", None)
            if not isinstance(session, AsyncSession):
                raise ValueError("Could not obtain a valid AsyncSession")

            inst = (
                f"{self.__class__.__module__}.{self.__class__.__name__}.{fn.__name__}"
            )
            if tag:
                inst += f"[{tag}]"

            tx_before = session.in_transaction()
            _log(
                f"[TX] ↩️  Enter {inst} | root={root} readonly={readonly} | tx_before={tx_before}"
            )

            if isolation or readonly_tx:
                conn = await session.connection()
                if isolation:
                    await conn.execution_options(isolation_level=isolation)
                    _log(f"[TX] 🛡️  Isolation → {isolation}", "INFO")
                if readonly_tx:
                    await conn.execute("SET TRANSACTION READ ONLY")
                    _log("[TX] 📖  READ ONLY", "INFO")

            async def _run_inner() -> T:
                start = time.perf_counter()
                try:
                    res = await fn(self, *args, **kwargs)
                    if raise_on_empty and res is None:
                        raise DatabaseException(
                            message="Entity not found",
                            details=f"{inst} returned None",
                            instance=inst,
                        )
                    return res
                finally:
                    _log(
                        f"[TX] ⏱️  Body took {time.perf_counter() - start:.4f}s", "DEBUG"
                    )

            async def _run_timeout() -> T:
                if timeout is None:
                    return await _run_inner()
                _log(f"[TX] ⏰  Timeout {timeout}s", "INFO")
                return await asyncio.wait_for(_run_inner(), timeout)

            async def _run_retries() -> T:
                attempt = 0
                while True:
                    try:
                        if attempt:
                            _log(f"[TX] 🔄  Retry {attempt}/{retries}", "INFO")
                        return await _run_timeout()
                    except OperationalError as oe:
                        if attempt >= retries or "deadlock" not in str(oe).lower():
                            raise
                        attempt += 1
                        await asyncio.sleep(0)

            _execute = _run_retries if retries else _run_timeout

            if root and not tx_before:
                _log("[TX] 🟢  Begin ROOT", "INFO")
                async with session.begin():
                    result = await _execute()
                _log("[TX] ✅  ROOT commit", "INFO")
                return result

            try:
                if savepoint and tx_before:
                    _log("[TX] 🪄  SAVEPOINT start", "INFO")
                    async with session.begin_nested():
                        result = await _execute()
                else:
                    result = await _execute()

                tx_after = session.in_transaction()
                self_started = (not tx_before) and tx_after

                if readonly:
                    if self_started:
                        _log("[TX] 👀  Read‑only → COMMIT", "INFO")
                        await session.commit()
                    elif auto_flush:
                        _log("[TX] 🔄  Read‑only → FLUSH", "DEBUG")
                        await session.flush()
                else:
                    if self_started:
                        _log("[TX] 💾  COMMIT", "INFO")
                        await session.commit()
                    elif auto_flush:
                        _log("[TX] 🔄  Flush outer tx", "DEBUG")
                        await session.flush()

                if expire_on_end is True:
                    session.expire_all()
                    _log("[TX] 🌀  Objects expired", "DEBUG")

                if auditable and self_started:
                    _log(f"[AUDIT] {inst} committed", "INFO")

                _log(f"[TX] ✅  {inst} finished", "DEBUG")
                return result

            except (IntegrityError, InvalidFieldException, SQLAlchemyError):
                raise
            except Exception as e:
                if not tx_before and session.in_transaction():
                    _log("[TX] ↩️  ROLLBACK", "INFO")
                    await session.rollback()
                _log(f"[TX] ❌  {inst} error: {e}", "INFO")
                raise

        return wrapper

    return decorator(func) if func else decorator
