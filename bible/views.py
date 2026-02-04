from django.shortcuts import render, get_object_or_404
from .models import BibleBook, BibleChapter, BibleVerse


def book_list(request):
    """List all 39 OT books ordered by order field."""
    books = BibleBook.objects.all().order_by("order")
    return render(request, "bible/book_list.html", {"books": books})


def chapter_list(request, book_slug):
    """List all chapters for the selected book."""
    book = get_object_or_404(BibleBook, slug=book_slug)
    chapters = book.chapters.all().order_by("number")
    return render(request, "bible/chapter_list.html", {"book": book, "chapters": chapters})


def chapter_view(request, book_slug, chapter_number):
    """Display all verses for the chapter with prev/next chapter arrows."""
    book = get_object_or_404(BibleBook, slug=book_slug)
    chapter = get_object_or_404(BibleChapter, book=book, number=chapter_number)
    verses = chapter.verses.all().order_by("number")

    # Compute prev/next chapter for arrows
    prev_chapter = None
    next_chapter = None

    # Previous chapter: same book prev, or previous book's last chapter
    prev_in_book = BibleChapter.objects.filter(book=book, number__lt=chapter_number).order_by("-number").first()
    if prev_in_book:
        prev_chapter = prev_in_book
    else:
        prev_book = BibleBook.objects.filter(order__lt=book.order).order_by("-order").first()
        if prev_book:
            last_ch = BibleChapter.objects.filter(book=prev_book).order_by("-number").first()
            prev_chapter = last_ch

    # Next chapter: same book next, or next book's first chapter
    next_in_book = BibleChapter.objects.filter(book=book, number__gt=chapter_number).order_by("number").first()
    if next_in_book:
        next_chapter = next_in_book
    else:
        next_book = BibleBook.objects.filter(order__gt=book.order).order_by("order").first()
        if next_book:
            first_ch = BibleChapter.objects.filter(book=next_book).order_by("number").first()
            next_chapter = first_ch

    return render(
        request,
        "bible/chapter_view.html",
        {
            "book": book,
            "chapter": chapter,
            "verses": verses,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
        },
    )
