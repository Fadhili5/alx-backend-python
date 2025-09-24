from datetime import datetime
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        with open("C:\\Users\\HP\\Desktop\\alx-backend-python\\Django-Middleware-0x03\\requests.log", "a") as log_file:
            log_file.write(log_entry)
        response = self.get_response(request)
        return response
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, request):
        current_hour = datetime.now().hour
        if not(18 <= current_hour < 21):
            return HttpResponseForbidden("Access to messaging app is restricted outside 9pm and 6pm")
        return self.get_response(request)
    
class OffensiveLanguageMiddleware:
    message_log = {}
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/api/messages/') and request.method == 'POST':
            ip = self.get_client_ip(request)
            now = datetime.now()
            self.cleanup(ip, now)
            if ip not in self.message_log:
                self.message_log[ip] = []
            self.message_log[ip] = [t for t in self.message_log[ip] if now - t < timedelta(minutes=1)]
            if len(self.message_log[ip]) >= 5:
                return HttpResponseForbidden("Message rate limit exceeded: Max 5 messages per minute.")
            self.message_log[ip].append(now)
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def cleanup(self, ip, now):
        #Remove timestamps older than 1 minute
        if ip in self.message_log:
            self.message_log[ip] = [t for t in self.message_log[ip] if now - t < timedelta(minutes=1)]