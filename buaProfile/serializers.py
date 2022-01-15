from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    
class buasSerializers(serializers.Serializer):
    # list=[firstName', 'lastName', 'ID', 'phoneNumber', 
        #   'email', 'latitude', 'longitude','verified']
    firstName=serializers.CharField(max_length=200)
    lastName=serializers.CharField(max_length=200)
    ID=serializers.IntegerField()
    phoneNumber=serializers.IntegerField()
    email=serializers.CharField(max_length=200)
    latitude=serializers.CharField(max_length=200)
    longitude=serializers.CharField(max_length=200)
    verified=serializers.IntegerField()