from django.core.exceptions import ValidationError

class ValidatorFileExtension:
    def validate_file_extension(value):
        import os

        extension = os.path.splitext(value.name)[1]
        valide_extension = [".pdf", ".doc", ".docx"]
        if extension.lower() not in valide_extension:
            raise ValidationError(
                "Les formats de fichers acceptés sont PDF , DOC , DOCX uniquement "
            )
