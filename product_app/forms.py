from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from product_app.models import Product, ProductImage, Category
from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CreateProductForm(forms.ModelForm):
    # images = MultipleFileField()

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                           'margin-bottom: '
                                                                                           '10px;'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                 'margin-bottom: '
                                                                                                 '10px;'}))

    size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                           'margin-bottom: '
                                                                                           '10px;'}), required=False)

    price = forms.DecimalField(decimal_places=2, max_digits=6,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                               'margin-bottom: '
                                                                                               '10px;'}))

    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 250px; '
                                                                                                    'margin-bottom: '
                                                                                                    '10px'}))

    class Meta:
        model = Product
        fields = ["name", "description", "price", 'quantity', "size", 'category', 'sub_category']


class ImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)


class UpdateProductForm(CreateProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category = self.instance.category  # Get the selected category from the instance
        self.fields['sub_category'].queryset = category.subcategories.all()
