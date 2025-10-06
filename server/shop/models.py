from django.db import models
import json

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    original_price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    sold_count = models.IntegerField(null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    labels = models.TextField(null=True, blank=True)  # JSON string for labels array

    def get_labels_list(self):
        """Convert JSON string to list"""
        if self.labels:
            try:
                return json.loads(self.labels)
            except json.JSONDecodeError:
                return []
        return []

    def set_labels_list(self, labels_list):
        """Convert list to JSON string"""
        if labels_list:
            self.labels = json.dumps(labels_list)
        else:
            self.labels = None

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
