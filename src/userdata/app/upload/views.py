from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse


def image_upload(request):
    if request.method == "POST" and request.FILES["image_file"]:
        image_file = request.FILES["image_file"]
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        image_url = fs.url(filename)
        print(image_url)
        return render(request, "upload.html", {
            "image_url": image_url
        })
    return render(request, "upload.html")

def example_view(request):
    if request.method == 'GET':
        # Generate a response (example JSON response here)
        data = {
            'message': 'BLABLABLA',
            'status': 'success'
        }
        return JsonResponse(data)
    else:
        # Handle unsupported methods if needed
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# Create your views here.
