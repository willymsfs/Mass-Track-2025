
from rest_framework import serializers
from .models import Priest, IntentionType, IntentionSource, MassIntention, PersonalMassIntention, FixedDateMassIntention, BulkMassIntention, MassCelebration, DailyStatus

class PriestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Priest
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        user = Priest.objects.create_user(**validated_data)
        return user

class IntentionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentionType
        fields = '__all__'

class IntentionSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentionSource
        fields = '__all__'

class MassIntentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MassIntention
        fields = '__all__'

class PersonalMassIntentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalMassIntention
        fields = '__all__'

class FixedDateMassIntentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedDateMassIntention
        fields = '__all__'

class BulkMassIntentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkMassIntention
        fields = '__all__'

class MassCelebrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MassCelebration
        fields = '__all__'

class DailyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStatus
        fields = '__all__'


