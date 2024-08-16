from rest_framework import serializers
from .models import Raffle, Ticket, Prize
from django.db.models import F
import uuid


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ['name', 'amount']


class RaffleSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    prizes = PrizeSerializer(many=True, required=True)
    available_tickets = serializers.IntegerField(required=False)

    class Meta:
        model = Raffle
        fields = ['id', 'name', 'total_tickets', 'available_tickets', 'winners_drawn', 'tickets', 'prizes']
        

    def validate(self, value):
        if not value['prizes']:
            raise serializers.ValidationError("No prizes")
        if sum([prize['amount'] for prize in value['prizes']]) > value['total_tickets']:
            raise serializers.ValidationError("Too many prizes")
        return value


    def create(self, validated_data):
        prizes_data = validated_data.pop("prizes")
        validated_data['available_tickets'] = validated_data['total_tickets']
        raffle = Raffle.objects.create(**validated_data)
        for prize_data in prizes_data:
            Prize.objects.create(raffle=raffle, **prize_data)
        return raffle


class RaffleWinnerSerializer(serializers.ModelSerializer):
    raffle_id = serializers.UUIDField()
    ticket_number = serializers.IntegerField(required=False)
    prize = serializers.CharField(required=False)

    class Meta:
        model = Ticket
        fields = ['raffle_id', 'ticket_number', 'prize', 'verification_code']


class TicketSerializer(serializers.ModelSerializer):
    raffle_id = serializers.UUIDField()
    ticket_number = serializers.IntegerField(required=False)
    verification_code = serializers.CharField(required=False)
    
    class Meta:
        model = Ticket
        fields = ['raffle_id', 'ticket_number', 'verification_code', 'ip_address']

    def create(self, validated_data):
        raffle = Raffle.objects.get(id=validated_data['raffle_id'])
        validated_data['ticket_number'] = raffle.get_ticket_number()
        ticket = Ticket.objects.create(**validated_data)
        raffle.available_tickets = F('available_tickets') - 1
        raffle.save()
        return ticket
    


    
class TicketVerificationSerializer(serializers.ModelSerializer):
    has_won = serializers.BooleanField(required=False, default=False)
    prize = serializers.CharField(required=False, default=None)
    ticket_number = serializers.IntegerField()
    verification_code = serializers.UUIDField()

    class Meta:
        model = Ticket
        fields = ['has_won', 'prize', 'ticket_number', 'verification_code']
