from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category with nested hierarchy support."""

    name = models.CharField("nome", max_length=200)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="categoria pai",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Baby product listing."""

    name = models.CharField("nome", max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField("descrição")
    price = models.DecimalField("preço", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("estoque", default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoria",
    )
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """Product image with ordering support."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="produto",
    )
    image = models.ImageField("imagem", upload_to="products/%Y/%m/")
    alt_text = models.CharField("texto alternativo", max_length=200, blank=True)
    order = models.PositiveIntegerField("ordem", default=0)

    class Meta:
        verbose_name = "imagem do produto"
        verbose_name_plural = "imagens do produto"
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} — Imagem {self.order}"
