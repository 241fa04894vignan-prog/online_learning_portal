from rest_framework  import serializers
from . models import registers
class student_serilizers(serializers.ModelSerializer):
    class Meta:
        model=registers
        fields='__all__'