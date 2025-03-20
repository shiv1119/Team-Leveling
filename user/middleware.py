from django.utils.timezone import now

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = now().isoformat()
            
            if not last_activity or (now() - now().fromisoformat(last_activity)).total_seconds() > 30:
                request.session['last_activity'] = current_time
                request.session.modified = True 

        return response
