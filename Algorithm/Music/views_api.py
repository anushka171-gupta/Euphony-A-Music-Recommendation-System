from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

class LoginView(APIView):

    def post(self, request):
        response = {}
        response['status'] = 500
        response['message'] = 'Something went wrong'

        try:
            data = request.data 

            # get username
            if data.get('username') is None:
                response['message'] = 'Username not found'
                raise Exception('Username not found')

            # get password
            if data.get('password') is None:
                response['message'] = 'password not found'
                raise Exception('password not found')

            # check if username is present or not
            check_user = User.objects.filter(username = data.get('username')).first()
            if check_user is None:
                response['message'] = 'Invalid Username'
                raise Exception('Invalid Username')

            # authenticate the user
            user = authenticate(username = data.get('username'), password = data.get('password'))

            # if user is valid then login the user
            if user:
                login(request, user)
                response['message'] = 'Welcome'
                response['status'] = 200

            # else raise exception of invalid password
            else:
                response['message'] = 'Invalid Password'
                raise Exception('Invalid Password')

        except Exception as e:
            print(e)

        return Response(response)

LoginView = LoginView.as_view()

class RegisterView(APIView):

    def post(self, request):
        response = {}
        response['status'] = 500
        response['message'] = 'Something Went Wrong'

        try:
            data = request.data 

            # get username
            if data.get('username') is None:
                response['message'] = 'Username Not Found'
                raise Exception('Username Not Found')
            
            # get password
            if data.get('password') is None:
                response['message'] = 'Password Not Found'
                raise Exception('Password Not Found')

            # check if user is already taken or not
            check_user = User.objects.filter(username = data.get('username')).first() 

            if check_user:

                # if username is already taken then report message
                response['message'] = 'Username Already Taken'
                raise Exception('Username Already Taken')

            # get useername, firstname, lastname and create user 
            user = User.objects.create(username = data.get('username'), first_name = data.get('first_name'), last_name = data.get('last_name'))
            user.set_password(data.get('password'))
            user.save()

            # login the user
            login(request, user)

            response['message'] = 'User Created'
            response['status'] = 200
 
        except Exception as e:
            print(e)

        return Response(response)

RegisterView = RegisterView.as_view()