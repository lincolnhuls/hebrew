from django.db import models


class BibleBook(models.Model):
    slug = models.SlugField(max_length=20, unique=True)   # e.g. 'gen'
    osis = models.CharField(max_length=10, unique=True)   # e.g. 'Gen'
    name_en = models.CharField(max_length=50)             # 'Genesis'
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name_en


class BibleChapter(models.Model):
    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE, related_name="chapters")
    number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [("book", "number")]
        ordering = ["book__order", "number"]

    def __str__(self):
        return f"{self.book.name_en} {self.number}"


class BibleVerse(models.Model):
    chapter = models.ForeignKey(BibleChapter, on_delete=models.CASCADE, related_name="verses")
    number = models.PositiveSmallIntegerField()
    text = models.TextField()

    class Meta:
        unique_together = [("chapter", "number")]
        ordering = ["chapter__book__order", "chapter__number", "number"]

    def __str__(self):
        return f"{self.chapter} : {self.number}"
