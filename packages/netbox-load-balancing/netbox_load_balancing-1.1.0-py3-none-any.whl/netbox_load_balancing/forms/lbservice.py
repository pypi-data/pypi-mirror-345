from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
    NetBoxModelFilterSetForm,
)

from tenancy.forms import TenancyForm, TenancyFilterForm
from utilities.forms.rendering import FieldSet, ObjectAttribute
from utilities.forms.fields import (
    DynamicModelChoiceField,
    TagFilterField,
    CommentField,
    CSVModelChoiceField,
)

from tenancy.models import Tenant

from netbox_load_balancing.models import (
    LBService,
    LBServiceAssignment,
)

__all__ = (
    "LBServiceForm",
    "LBServiceFilterForm",
    "LBServiceImportForm",
    "LBServiceBulkEditForm",
    "LBServiceAssignmentForm",
)


class LBServiceForm(TenancyForm, NetBoxModelForm):
    name = forms.CharField(max_length=255, required=True)
    reference = forms.CharField(max_length=255, required=True)
    description = forms.CharField(max_length=200, required=False)
    disabled = forms.BooleanField(required=False)
    fieldsets = (
        FieldSet("name", "reference", "description", "disabled", name=_("LB Service")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )
    comments = CommentField()

    class Meta:
        model = LBService
        fields = [
            "name",
            "reference",
            "description",
            "disabled",
            "tenant_group",
            "tenant",
            "comments",
            "tags",
        ]


class LBServiceFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = LBService
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "reference", name=_("LB Service")),
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
    )
    tags = TagFilterField(model)


class LBServiceImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Tenant"),
    )

    class Meta:
        model = LBService
        fields = (
            "name",
            "reference",
            "description",
            "disabled",
            "tenant",
            "tags",
        )


class LBServiceBulkEditForm(NetBoxModelBulkEditForm):
    model = LBService
    reference = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=200, required=False)
    disabled = forms.BooleanField(required=False)
    tags = TagFilterField(model)
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )
    nullable_fields = ["description"]
    fieldsets = (
        FieldSet("reference", "description", "disabled", name=_("LB Service")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )


class LBServiceAssignmentForm(forms.ModelForm):
    service = DynamicModelChoiceField(
        label=_("LB Service"), queryset=LBService.objects.all()
    )

    fieldsets = (FieldSet(ObjectAttribute("assigned_object"), "service"),)

    class Meta:
        model = LBServiceAssignment
        fields = ("service",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_service(self):
        service = self.cleaned_data["service"]

        conflicting_assignments = LBServiceAssignment.objects.filter(
            assigned_object_type=self.instance.assigned_object_type,
            assigned_object_id=self.instance.assigned_object_id,
            service=service,
        )
        if self.instance.id:
            conflicting_assignments = conflicting_assignments.exclude(
                id=self.instance.id
            )

        if conflicting_assignments.exists():
            raise forms.ValidationError(_("Assignment already exists"))

        return service
