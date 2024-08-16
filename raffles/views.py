from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from .models import Raffle, Ticket, Prize
from .serializers import RaffleSerializer, TicketSerializer, PrizeSerializer, RaffleWinnerSerializer, TicketVerificationSerializer
from .permissions import IsManagerIP


class RaffleView(RetrieveAPIView):
    permission_classes = []
    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer
    lookup_field = "id"


class AllRafflesView(ListCreateAPIView):
    permission_classes = [IsManagerIP]
    queryset = Raffle.objects.all().order_by('-created_at')
    serializer_class = RaffleSerializer
    lookup_field = "id"

# class AllRafflesView(APIView):
#     permission_classes = [IsManagerIP]
#     def get(self, request, *args, **kwargs):
#         queryset = Raffle.objects.all().order_by('-created_at')
#         serializer = RaffleSerializer (queryset, many=True)
#         return Response(serializer.data)
    
#     def post(self, request, *args, **kwargs):
#         serializer = RaffleSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParticipateView(APIView):

    permission_classes = []

    def post(self, request, *args, **kwargs):
        raffle_id = self.kwargs['id']
        raffle = get_object_or_404(Raffle, pk=raffle_id)

        isAvailable = raffle.available_tickets > 0
        if not isAvailable:
            return Response({"Tickets to this raffle are no longer available"}, status=status.HTTP_410_GONE)

        user_ip = request.META.get('REMOTE_ADDR')
        hasParticipated = raffle.tickets.filter(ip_address=user_ip).exists()
        if hasParticipated:
            return Response({'error': 'Your ip address has already participated in this raffle'}, status=status.HTTP_403_FORBIDDEN)
        
        data = {
            'ip_address': user_ip,
            'raffle_id': raffle_id
        }
        data.update(request.data)

        serializer = TicketSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WinnersView(APIView):

    permission_classes = [IsManagerIP]

    def get(self, request, *args, **kwargs):
        raffle = get_object_or_404(Raffle, pk=kwargs['id'])
        winners = raffle.tickets.filter(has_won=True)
        if not winners:
            return Response({"Winners for the raffle have not been drawn yet"}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = RaffleWinnerSerializer(winners, many=True)
        return Response(serializer.data)
        # queryset = Raffle.objects.get(pk=kwargs['id']).tickets.filter(has_won=True)
        # serializer = TicketSerializer(queryset, many=True)
        # return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        raffle = get_object_or_404(Raffle, pk=kwargs['id'])
        if raffle.available_tickets != 0:
            return Response({"Winners can't be drawn when tickets are still available"}, status=status.HTTP_403_FORBIDDEN)
    
        if raffle.winners_drawn == True:
            return Response({"Winners for the raffle have already been drawn"}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = raffle.draw_winners()
        serializer = RaffleWinnerSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VerifyTicketView(APIView):
    def post(self, request, *args, **kwargs):
        raffle = get_object_or_404(Raffle, pk=kwargs['id'])
        if raffle.winners_drawn == False:
            return Response({"Winners for the raffle have not been drawn yet"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            verification_code = request.data['verification_code']
            ticket_number=request.data['ticket_number']
            queryset = Ticket.objects.get(
                verification_code=verification_code,
                ticket_number=ticket_number)
            serializer = TicketVerificationSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"Invalid verification code/Invalid ticket number"}, status=status.HTTP_400_BAD_REQUEST)