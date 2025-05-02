from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator

from hs_django_ckeditor.validators import FileMaxSizeValidator


class UploadFileForm(forms.Form):
    upload = forms.FileField(
        validators=[
            FileExtensionValidator(
                getattr(
                    settings,
                    "CKEDITOR_5_UPLOAD_FILE_TYPES",
                    ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"],
                ),
            ),
            FileMaxSizeValidator(getattr(settings, "CKEDITOR_5_MAX_FILE_SIZE", 0)),
        ],
    )
