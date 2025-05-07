from typing_extensions import Callable, Tuple, Any


def get_memory_usage(
    func: Callable,
    args: Tuple[Any] = (),
    kwargs: dict[str, Any] = {},
    unit: int = 1024**2,
):
    import tracemalloc

    tracemalloc.start()

    # 记录导入前内存快照
    before_snapshot = tracemalloc.take_snapshot()

    func(*args, **kwargs)

    after_snapshot = tracemalloc.take_snapshot()

    total_increase = sum(
        stat.size_diff
        for stat in after_snapshot.compare_to(before_snapshot, "traceback")
    )
    return total_increase / unit, after_snapshot.compare_to(before_snapshot, "lineno")
