from django.test import TestCase
from django.urls import reverse_lazy
from apps.bmui.models import BOMLevel
from django_starter.contrib.seed import Seeder


# Create your tests here.
class Test(TestCase):
    def setUp(self):
        self.seeder = Seeder()

        instances = []
        for i in range(10):
            instances.append(BOMLevel(**self.seeder.seed(BOMLevel)))
        BOMLevel.objects.bulk_create(instances)

    def test_query(self):
        self.assertGreaterEqual(BOMLevel.objects.count(), 10)

    def test_api_create(self):
        data = self.seeder.seed(BOMLevel)
        resp = self.client.post(
            reverse_lazy('api:bmui/bom_level/create'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

        return resp.json()

    def test_api_retrieve(self):
        item = self.test_api_create()
        resp = self.client.get(reverse_lazy('api:bmui/bom_level/retrieve', kwargs={'item_id': item['data']['id']}))
        self.assertEqual(resp.status_code, 200)

    def test_api_list(self):
        resp = self.client.get(reverse_lazy('api:bmui/bom_level/list'))
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.json()['data']['count'], 10)

    def test_api_update(self):
        item = self.test_api_create()
        data = self.seeder.seed(BOMLevel)
        resp = self.client.put(
            reverse_lazy('api:bmui/bom_level/update', kwargs={'item_id': item['data']['id']}),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

    def test_api_partial_update(self):
        item = self.test_api_create()
        data = self.seeder.seed(BOMLevel)
        resp = self.client.patch(
            reverse_lazy('api:bmui/bom_level/partial_update', kwargs={'item_id': item['data']['id']}),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

    def test_api_destroy(self):
        item = self.test_api_create()
        resp = self.client.delete(
            reverse_lazy('api:bmui/bom_level/destroy', kwargs={'item_id': item['data']['id']}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

        resp = self.client.get(reverse_lazy('api:bmui/bom_level/retrieve', kwargs={'item_id': item['data']['id']}))
        self.assertEqual(resp.status_code, 404)