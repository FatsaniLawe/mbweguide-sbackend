import os
import joblib
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CommunityChatMessage
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from .expert_logic import get_crop_section, get_crop_stages

# Load the model once at import time
MODEL_PATH = os.path.join(settings.BASE_DIR, 'api', 'ml_models', 'random_forest_model.pkl')
try:
    crop_model = joblib.load(MODEL_PATH)
    print(f"Crop model loaded from: {MODEL_PATH}")
except Exception as e:
    crop_model = None
    print(f"Failed to load crop model: {e}")

# Example: Load a chatbot ML model (replace with your actual model path and logic)
CHATBOT_MODEL_PATH = os.path.join(settings.BASE_DIR, 'api', 'ml_models', 'chatbot_model.joblib')
try:
    chatbot_model = joblib.load(CHATBOT_MODEL_PATH)
    print(f"Chatbot model loaded from: {CHATBOT_MODEL_PATH}")
except Exception as e:
    chatbot_model = None
    print(f"Failed to load chatbot model: {e}")

class RecommendCropView(APIView):
    def post(self, request):
        if crop_model is None:
            return Response({"error": "Model not loaded"}, status=500)

        try:
            N = float(request.data.get("N"))
            P = float(request.data.get("P"))
            K = float(request.data.get("K"))
            temperature = float(request.data.get("temperature"))
            humidity = float(request.data.get("humidity"))
            ph = float(request.data.get("pH"))
            rainfall = float(request.data.get("rainfall"))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid input. All fields must be numbers: N, P, K, temperature, humidity, pH, rainfall."},
                status=400
            )

        try:
            # Prepare input for prediction
            import pandas as pd

            features = pd.DataFrame([{
                    'N': N,
                    'P': P,
                    'K': K,
                    'temperature': temperature,
                    'humidity': humidity,
                    'ph': ph,
                    'rainfall': rainfall
                }])


            # Predict probabilities for all classes
            classes = crop_model.classes_
            probabilities = crop_model.predict_proba(features)[0]

            # Sort and get top 3 predictions
            top_predictions = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)[:3]

            return Response({
                "recommendations": [
                    {"crop": crop, "probability": round(prob * 100, 2)}
                    for crop, prob in top_predictions
                ]
            })
        except Exception as e:
            return Response({"error": f"Prediction error: {str(e)}"}, status=500)



class HealthCheckView(APIView):
    def get(self, request):
        status = "ok" if crop_model is not None else "model_not_loaded"
        return Response({"status": status})


class CommunityChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityChatMessage
        fields = ['id', 'user', 'message', 'timestamp']


class CommunityChatPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommunityChatHistoryView(APIView):
    def get(self, request):
        messages = CommunityChatMessage.objects.order_by('timestamp')
        paginator = CommunityChatPagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = CommunityChatMessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ChatbotView(APIView):
    def post(self, request):
        if chatbot_model is None:
            return Response({'error': 'Chatbot model not loaded'}, status=500)
        user_message = request.data.get('message', '').strip()
        if not user_message:
            return Response({'error': 'No message provided.'}, status=400)
        try:
            # Example: If your model has a .predict method
            # Adapt this to your actual model's API
            response = chatbot_model.predict([user_message])[0]
            return Response({'response': response})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .expert_logic import get_crop_section, get_crop_stages

logger = logging.getLogger(__name__)

class ExpertSystemView(APIView):
    def get(self, request):
        crop = request.GET.get('crop')
        section = request.GET.get('section')

        if not crop:
            return Response(
                {"error": "Missing required 'crop' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Case: Crop and Section provided (return advice for section)
            if section:
                advice = get_crop_section(crop, section)
                if advice:
                    return Response({
                        "crop": crop,
                        "section": section,
                        "advice": advice
                    })
                else:
                    return Response({
                        "error": f"No advice found for crop '{crop}' and section '{section}'"
                    }, status=status.HTTP_404_NOT_FOUND)

            # Case: Only crop provided (return stages)
            stages = get_crop_stages(crop)
            if stages:
                return Response({
                    "crop": crop,
                    "stages": stages
                })
            else:
                return Response({
                    "error": f"No stages found for crop '{crop}'."
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error in ExpertSystemView for crop='{crop}' section='{section}': {e}", exc_info=True)
            return Response({
                "error": "Internal server error. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
