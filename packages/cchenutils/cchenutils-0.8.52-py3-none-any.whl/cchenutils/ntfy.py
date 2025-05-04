from .session import Session


def push(topic, title, content):
    with Session(timeout=10) as sess:
        url = f'https://ntfy.sh/{topic}'
        data = content
        headers={'Title': f'{title}'}
        sess.post(url, data=data, headers=headers)
