"""
Оптимізувати клас EventAggregator для мінімізації копій памʼяті.

Завдання:
    Поточна реалізація EventAggregator створює багато непотрібних копій. Потрібно
    переписати логіку так, щоб обробка подій була максимально ефективною за памʼяттю.

Вимоги:
    - Назва класу EventAggregator та метод __init__ мають залишитися незмінними;
    - Метод run() має бути присутнім; його вміст можна змінювати за потреби;
    - Більше обмежень по модифікаціям у класі немає;
    - Мета - мінімізувати алокації, копії в памʼяті;
    - Фінальний результат має формувати payload по користувачах у тому ж форматі.

Актуальність:
    Робота з великими JSON-потоками та S3 - типова задача в системах обробки подій.
    Надмірні копії призводять до високого споживання памʼяті та CPU.
    Оптимізація дозволяє побудувати ефективний pipeline і продемонструвати
    практичне розуміння методів мінімізації алокацій та роботи зі структурами даних у Python.
"""

import json

from datetime import datetime

from memory.fragments_and_copies.homework import fake_boto3


class EventAggregator:  # <- Залиш назву незмінною
    def __init__(self, bucket: str, prefix: str):  # <- Init метод має залишитися таким
        self.bucket = bucket
        self.prefix = prefix

        self.s3 = fake_boto3.client('s3')

    def run(self) -> list[dict]:  # <- метод run має бути наявним у класі, вміст можна змінювати за потреби
        objects = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix,
        )['Contents']

        payload_by_user: dict[str, dict] = {}

        for obj in objects:
            raw = self.s3.get_object(
                Bucket=self.bucket,
                Key=obj['Key'],
            )['Body'].read()

            events = json.loads(raw)

            for event in events:
                event['timestamp'] = datetime.fromisoformat(event['timestamp']).timestamp()
                event.setdefault('extra', {})

                user = event['user_id']
                rec = payload_by_user.get(user)
                if rec is None:
                    rec = {'user': user, 'count': 0, 'events': []}
                    payload_by_user[user] = rec

                rec['events'].append(event)
                rec['count'] += 1

        return list(payload_by_user.values())
