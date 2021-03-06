import datetime,os
from django import forms
from django.shortcuts import render
from django.core.urlresolvers import reverse,reverse_lazy
from django.core.signing import Signer
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Q
from HotelApp.models import Hotels,Room,Proposal
from Authorize.models import UserRole
from ManageHotels.models import Photo
from Reservations.models import Reservation
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.template.loader import get_template
from .utils import render_to_pdf
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import boto3,botocore,json
from xhtml2pdf import pisa
ACCESS='AKIAIZGUB7EMMDIMH7CA'
SECRET='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'
region='us-east-1'
import MailConfig as MUE_Config
import MailUtils
import MySQLdb
conn = MySQLdb.connect('10.0.2.239','root','Priya@123','airbnb')
curs = conn.cursor()

## Generates a PDF using the render help function and outputs it as invoice.html
class GeneratePDF(View):
    def get(self,request, *args, **kwargs):
        booking = Reservation.objects.get(id= self.kwargs['id'])
        template = get_template('invoice.html')
        context = {"booking":booking}
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
	outputFilename=os.path.join("/tmp/","invoice.pdf")
	resultFile = open(outputFilename, "w+b")
	pisaStatus = pisa.CreatePDF(html,dest=resultFile)
	resultFile.close() 
#	pisa.CreatePDF(StringIO(html.encode('utf-8')), pdffile)
        files = []
        to = []
        files.append(outputFilename)
        email_query = "select email from auth_user a join Reservations_reservation b on a.id=b.user_id where a.id = '%s'"%(self.kwargs['id'])
        curs.execute(email_query)
        to_email = curs.fetchall()
        to.append(to_email[0][0])
#        print outputFilename
#        print files
#        print to
        MailUtils.send_mail(MUE_Config.MailConfig['auth'], MUE_Config.MailConfig['from'],to ,MUE_Config.MailConfig['subject'],MUE_Config.MailConfig['content'], None, files,cc=MUE_Config.MailConfig['cc'])

#	pdfile=open("PDF_BOOKING%s.pdf"%(self.kwargs['id']))
#	filename="PDF_BOOKING%s.pdf"%(self.kwargs['id'])
	s3=boto3.client('s3',aws_access_key_id=ACCESS,aws_secret_access_key=SECRET,region_name=region,config=boto3.session.Config(signature_version='s3v4'))
#        return HttpResponse(pdf,content_type='application/pdf')
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="BookingReceipt.pdf"'
	s3.upload_file(outputFilename,'airbnbgokulb',self.kwargs['id']+'BookingReceipt.pdf')
	return response


@api_view(['POST'])
@csrf_exempt
def bookingsns(request):
	print request
	if request.method=='POST':
		received_json_data=json.loads(request.body)
		print received_json_data
		topic="arn:aws:sns:us-east-1:165910365825:bookingconfirmed"
		if received_json_data['Type']=='SubscriptionConfirmation':
			Token_Received=received_json_data['Token']
			snsclient=boto3.client('sns',aws_access_key_id=ACCESS,aws_secret_access_key=SECRET,region_name=region,config=boto3.session.Config(signature_version='s3v4'))
			response = snsclient.confirm_subscription(TopicArn=topic,Token=Token_Received, AuthenticateOnUnsubscribe='true')
			return HttpResponse("200 OK")
		elif received_json_data['Type']=='Notification':
			a=received_json_data
			MessageReceived = json.loads(a['Message'])
			BUCKET_ARN= MessageReceived['Records'][0]['s3']['bucket']['arn']
			BUCKET_NAME=MessageReceived['Records'][0]['s3']['bucket']['name']
			KEY= str(MessageReceived['Records'][0]['s3']['object']['key'])
			s3=boto3.client('s3',aws_access_key_id=ACCESS,aws_secret_access_key=SECRET,region_name=region,config=boto3.session.Config(signature_version='s3v4'))
			print BUCKET_ARN,BUCKET_NAME,KEY
			try:
				s3.download_file(BUCKET_NAME,KEY,KEY)
		#		s3.download_file('airbnbgokul','2invoice.pdf','2invoice.pdf')
#				sendmail()
			except botocore.exceptions.ClientError as e:
				if e.response['Error']['Code']=="404":
					print("The object does not exist")
				else:
					raise
			return HttpResponse("200 OK")


## Works out how long the user is staying in a hotel for also working out the total cost.
def bookRoom(request,hotelid,roomid):

    FirstDate = request.session['checkin']
    SecDate =  request.session['checkout']

    Checkin = datetime.datetime.strptime(FirstDate, "%Y-%m-%d").date()
    Checkout = datetime.datetime.strptime(SecDate, "%Y-%m-%d").date()
    timedeltaSum = Checkout - Checkin

    StayDuration = timedeltaSum.days

    Hotel = Hotels.objects.get(id = hotelid)
    theRoom = Room.objects.get(id = roomid)

    price = theRoom.Price
    TotalCost = StayDuration * price


    context = {'checkin': Checkin, 'checkout':Checkout,'stayduration':StayDuration,'hotel':Hotel,'room':theRoom,'price':price,
    'totalcost':TotalCost}
    return render(request, 'Reservations/booking.html', context)

# Stores the confirmed booking  into the database
def storeBooking(request,hotelid,roomid,checkin,checkout,totalcost):
    if request.method == 'POST':

        Firstname = request.POST.get('firstname')
        Lastname = request.POST.get('lastname')
        user = request.user
        hotel = Hotels.objects.get(id = hotelid)
        room = Room.objects.get(id = roomid)
        cost = totalcost
        newReservation = Reservation()
        newReservation.hotel = hotel
        newReservation.room = room
        newReservation.user = user
        newReservation.guestFirstName = Firstname
        newReservation.guestLastName = Lastname
        newReservation.CheckIn = checkin
        newReservation.CheckOut = checkout
        newReservation.totalPrice = cost
        newReservation.save()
        #Deletes the session variables.
        del request.session['checkin']
        del request.session['checkout']
        link = reverse('HotelApp:userDash')
        return HttpResponseRedirect(link)

    else:
        url = reverse('HotelApp:userDash')
        return url

#Shows the user thier previous bookings.
def mybookings(request):
    bookings = Reservation.objects.filter(user = request.user)
    context = {'bookings':bookings}
    return render(request, 'Reservations/mybookings.html', context)


# Allows a user to cancel their previous bookings , deleting a booking onclick.
def cancelbooking(request,id):
    booking = Reservation.objects.get(id = id)
    booking.delete()
    currentuser = request.user
    Role = UserRole.objects.get(user = request.user)
    link = reverse('Reservations:viewbookings')
    return HttpResponseRedirect(link)
