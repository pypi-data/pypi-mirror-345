# DRF Verbose Serializers

A Django REST Framework extension that allows you to use verbose field names in your serializers.

## Installation

```bash
pip install drf-verbose-serializers
```

## Features

- Adds `verbose_field_name` parameter to DRF serializer fields
- Allows customizing serializer output field names without changing the underlying model or serializer field names
- Supports nested serializers with many=True relationships
- Includes mixins for both ModelSerializer and Serializer classes

## Usage

### Basic Example

```python
from rest_framework import serializers
from drf_verbose_serializers import VerboseModelSerializerMixin, VerboseCharField, VerboseIntegerField

class UserSerializer(VerboseModelSerializerMixin, serializers.ModelSerializer):
    username = VerboseCharField(verbose_field_name='Username')
    email = VerboseCharField(verbose_field_name='Email Address')
    age = VerboseIntegerField(verbose_field_name='Age')

    class Meta:
        model = User
        fields = ['username', 'email', 'age']
```

This will produce JSON like:

```json
{
    "Username": "johndoe",
    "Email Address": "john@example.com",
    "Age": 30
}
```

### Using with Regular Serializers

```python
from rest_framework import serializers
from drf_verbose_serializers import VerboseSerializerMixin, VerboseCharField, VerboseIntegerField

class UserSerializer(VerboseSerializerMixin, serializers.Serializer):
    username = VerboseCharField(verbose_field_name='Username')
    email = VerboseCharField(verbose_field_name='Email Address')
    age = VerboseIntegerField(verbose_field_name='Age')
```

### Nested Serializers

```python
from rest_framework import serializers
from drf_verbose_serializers import (
    VerboseModelSerializerMixin, 
    VerboseCharField,
    VerbosePrimaryKeyRelatedField
)

class CommentSerializer(VerboseModelSerializerMixin, serializers.ModelSerializer):
    text = VerboseCharField(verbose_field_name='Comment Text')
    
    class Meta:
        model = Comment
        fields = ['text']

class PostSerializer(VerboseModelSerializerMixin, serializers.ModelSerializer):
    title = VerboseCharField(verbose_field_name='Post Title')
    body = VerboseCharField(verbose_field_name='Post Body')
    comments = CommentSerializer(many=True, verbose_field_name='Post Comments')
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'comments']
```

## Available Fields

All standard DRF fields are supported with verbose name variants:

- VerboseCharField
- VerboseIntegerField
- VerboseBooleanField
- VerboseDateTimeField
- VerboseDateField
- VerboseFloatField
- VerboseDecimalField
- VerboseEmailField
- VerboseSerializerMethodField
- VerboseRelatedField
- VerbosePrimaryKeyRelatedField
- VerboseHyperlinkedRelatedField
- VerboseSlugRelatedField
- VerboseHyperlinkedIdentityField
- VerboseListField
- VerboseDictField
- VerboseJSONField
- VerboseStringRelatedField

## License

MIT 