from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . models import registers
from . serializers import student_serilizers
@api_view(['GET'])
def student_view(request):
    student=registers.objects.all()
    ss=student_serilizers(
        student,
        many=True
    
    )
    return Response(ss.data)
def register(request):
    return render(request, 'signup.html')
