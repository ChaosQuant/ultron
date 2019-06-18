import sys
sys.path.append('../..')
from ultron.cluster.invoke.submit_tasks import submit_task

if __name__ == "__main__":
    submit_task.submit_packet('dk', 'jpy')