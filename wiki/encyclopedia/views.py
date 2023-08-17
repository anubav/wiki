from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from . import util
import markdown2
import random


class SearchForm(forms.Form):
    query = forms.CharField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Search Encyclopedia"})
    )


class EntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="", widget=forms.Textarea)
    new = forms.BooleanField(required=False, initial=True, widget = forms.HiddenInput())


def index(request):
    query = ""
    all_entries = util.list_entries()
    search = request.method == "POST"
    if search:
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            if query.lower() in map(lambda title: title.lower(), all_entries):
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=[query]))

    entries = list(
        sorted(filter(lambda title: query.lower() in title.lower(), all_entries))
    )
    entries_with_urls = map(
        lambda title: {
            "title": title,
            "url": reverse("encyclopedia:entry", args=[title]),
        },
        entries,
    )

    return render(
        request,
        "encyclopedia/index.html",
        {
            "query": query,
            "form": SearchForm(),
            "search": search,
            "entries": entries_with_urls,
            "random": reverse("encyclopedia:entry", args=[random.choice(entries)]),
        },
    )


def entry(request, title):
    md_content = util.get_entry(title)
    if md_content == None:
        return render(
            request,
            "encyclopedia/error.html",
            {"form": SearchForm(), "message": "The requested page was not found"},
        )
    else:
        return render(
            request,
            "encyclopedia/entry.html",
            {
                "form": SearchForm(),
                "title": title,
                "content": mark_safe(markdown2.markdown(md_content)),
            },
        )

def edit(request, title):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data
            if entry["new"] and (entry["title"].lower() in map(lambda title: title.lower(), util.list_entries())):
                return render(
                    request,
                    "encyclopedia/error.html",
                    {"form": SearchForm(), "message": "The page already exists"},
                )
            else:
                util.save_entry(entry["title"], entry["content"])
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=[entry["title"]]))
        else: 
            return render(
                    request,
                    "encyclopedia/error.html",
                    {"form": SearchForm(), "message": form.errors},
                )
    else:
        if title == None:
            entry_form = EntryForm()
        else:
            md_content = util.get_entry(title)
            entry_form = EntryForm(
                {"title": title, 
                 "content": md_content, 
                 "new": False}
            )
            entry_form.fields["title"].widget.attrs["readonly"] = True
        return render(
            request,
            "encyclopedia/edit.html",
            {"title": title, "form": SearchForm(), "entry_form": entry_form},
        )
