from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        # UniqueConstraint on the model is not auto-promoted to a DRF validator,
        # so declare it explicitly to return 400 instead of an IntegrityError.
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=["company", "name"],
                message="A category with this name already exists for this company.",
            )
        ]

    def validate(self, attrs):
        parent = attrs.get("parent_category")
        company = attrs.get("company") or getattr(self.instance, "company", None)
        if parent is not None and company is not None and parent.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "parent_category must belong to the same company."}
            )
        if self.instance is not None and parent is not None and parent.id == self.instance.id:
            raise serializers.ValidationError(
                {"parent_category": "parent_category must not be itself."}
            )
        return attrs
