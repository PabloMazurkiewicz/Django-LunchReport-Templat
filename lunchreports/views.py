from django.shortcuts import render
from django.views import View
from .models import Student, Teacher, LunchItem, LunchItemOrder
from django.core.exceptions import ValidationError
from .generate_report import populate_pdf_response
from collections import defaultdict
from decimal import Decimal
import logging  #noqa


def index(request):
  return render(request, 'index.html')


def _get_lunch_items_from_request(request):
  lunch_item_names = ",".join(request.GET.getlist('lunch_items'))
  lunch_item_names = lunch_item_names.split(",")
  lunch_item_model_list = list(
      LunchItem.objects.filter(name__in=lunch_item_names))
  if len(lunch_item_model_list) <= 0:
    return list(LunchItem.objects.all())
  return lunch_item_model_list


# @Author: Dias
# @Date: 6/13/2024
# @Desc: Convert default to regular dictionary.
def _default_to_regular_dict(d):
    if isinstance(d, defaultdict):
        d = {k: _default_to_regular_dict(v) for k, v in d.items()}
    return d

# @Author: Dias
# @Date: 6/22/2024
# @Desc: Fetch lunch data.
def _get_lunch_data(lunch_item_model_list, combined=False):
    # Initialize nested defaultdict with int as default factory
    lunch_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
    
    if combined:
        # Fetch all orders for the given lunch items in the list
        orders = LunchItemOrder.objects.filter(lunch_item__in=lunch_item_model_list)
        table_title = ", ".join(str(item) for item in lunch_item_model_list)
    else:
        # Fetch orders for each item individually
        orders = LunchItemOrder.objects.filter(lunch_item__in=lunch_item_model_list)
    
    for order in orders:
        if order.student:
            teacher_name = order.student.teacher.name if order.student.teacher else '-'
            orderer_name = order.student.name
        else:
            teacher_name = order.teacher.name
            orderer_name = teacher_name
        
        item_name = order.lunch_item.name
        
        if combined:
            lunch_data[table_title][teacher_name][orderer_name][item_name] += order.quantity
        else:
            lunch_data[item_name][teacher_name][orderer_name][item_name] += order.quantity
        
    return lunch_data


# @Author: Dias
# @Date: 6/13/2024
# @Desc: Handle the request of "/"
def lunch_report(request):
  lunch_item_model_list = _get_lunch_items_from_request(request)
  lunch_data = _get_lunch_data(lunch_item_model_list)
  
  return populate_pdf_response(
      report_title="Lunch Order Report by Item",
      report_template="lunchreports/templates/lunch_order_report.html",
      data=_default_to_regular_dict(lunch_data)
  )  


def combined_lunch_report(request):
  lunch_item_model_list = _get_lunch_items_from_request(request)
  lunch_data = _get_lunch_data(lunch_item_model_list, True)

  return populate_pdf_response(
      report_title="Combined Lunch Order Report",
      report_template="lunchreports/templates/lunch_order_report.html",
      data=_default_to_regular_dict(lunch_data)
  )

