# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import os
import string
import random
import analyser
from .forms import FileUploadForm


def handle_uploaded_file(f):
    filename = "%s.csv" % ''.join(random.choice(
        string.ascii_uppercase +
        string.digits) for _ in range(8))
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return filename


# Create your views here.


def index(request):

    if request.method == "POST":
        if request.FILES:
            form = FileUploadForm(request.POST, request.FILES)

            rawdata = handle_uploaded_file(request.FILES["rawdata"])
            groups = handle_uploaded_file(request.FILES["groups"])

            user_data, group_data = analyser.analyse(rawdata, groups)

            for group in group_data:
                if group_data[group]["rank"] == 1:
                    winning_group = group

            # Give each user a score
            for user in user_data:
                user_data[user]["score"] = user_data[user]["average_brush_time"] * user_data[user]["total_brushes"] * user_data[user]["twice_brushes"]

            # Delete CSV files
            os.remove(rawdata)
            os.remove(groups)

            context = {
                'user_data': user_data,
                'group_data': group_data,
                'winning_group': winning_group,
            }

            return render(request, 'analyse/analysis.html', context)
    else:
        form = FileUploadForm()

        context = {
            'form': form,
        }
    return render(request, 'analyse/index.html', context)
