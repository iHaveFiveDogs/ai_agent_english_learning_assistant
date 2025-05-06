import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def update_progress(job_id: str, percent: int):
    current = r.get(job_id)
    print(f"[DEBUG] Before update: job_id={job_id}, current={current}, new={percent}")
    if current is None or int(current) < percent:
        r.set(job_id, percent, ex=3600) # Expires after 1 hour
        print(f"[DEBUG] Updated Redis: job_id={job_id}, percent={percent}")
    else:
        print(f"[DEBUG] Not updated: job_id={job_id}, current={current}, new={percent}")

def get_progress(job_id: str) -> int:
    value = r.get(job_id)
    print(f"[DEBUG] get_progress: job_id={job_id}, value={value}")
    return int(value) if value else 0

def reset_progress(job_id: str):
    r.delete(job_id)
    print(f"[DEBUG] reset_progress: job_id={job_id} deleted")


def delete_progress(job_id: str):
    r.delete(job_id)