from rest_framework import serializers

class AudioSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    audio_raw = serializers.ListField(child=serializers.FloatField())
    sample_rate = serializers.IntegerField()

    def create(self, validated_data):
        audio = {
            'name': validated_data['name'],
            'audio_raw': validated_data['audio_raw'],
            'sample_rate': validated_data['sample_rate']
        }

        return audio
