from rest_framework import serializers


class VerboseModelSerializerMixin:
    """
    A mixin for ModelSerializer that allows specifying verbose_field_name
    for fields and uses them in the JSON output.

    Usage:
        class MySerializer(VerboseNameModelSerializerMixin, ModelSerializer):
            field = serializers.CharField(verbose_field_name='Fancy_Name')
    """
        
    def to_representation(self, instance):
        """
        Override the to_representation method to transform field names
        based on the verbose_field_name attribute if provided.
        """
        # Get the default representation
        representation = super().to_representation(instance)
            
        # Create a new representation with possibly renamed fields
        verbose_representation = {}
        
        # Get all declared fields in the serializer
        for field_name, field in self.fields.items():
            # Check if the field has a verbose_field_name attribute
            verbose_name = getattr(field, 'verbose_field_name', None)
            output_name = verbose_name if verbose_name else field_name
            
            # If field_name is in representation, add it to verbose_representation
            if field_name in representation:
                verbose_representation[output_name] = representation[field_name]
        
        return verbose_representation


class VerboseSerializerMixin:
    """
    A mixin for Serializer that allows specifying verbose_field_name
    for fields and uses them in the JSON output.

    Usage:
        class MySerializer(VerboseNameSerializerMixin, Serializer):
            field = serializers.CharField(verbose_field_name='Fancy_Name')
    """
        
    def to_representation(self, instance):
        """
        Override the to_representation method to transform field names
        based on the verbose_field_name attribute if provided.
        """
        # Get the default representation
        representation = super().to_representation(instance)
            
        # Create a new representation with possibly renamed fields
        verbose_representation = {}
        
        # Get all declared fields in the serializer
        for field_name, field in self.fields.items():
            # Check if the field has a verbose_field_name attribute
            verbose_name = getattr(field, 'verbose_field_name', None)
            output_name = verbose_name if verbose_name else field_name
            
            # If field_name is in representation, add it to verbose_representation  
            if field_name in representation:
                verbose_representation[output_name] = representation[field_name]
        
        return verbose_representation


# Override serializer that is used for many=True nested relationships
class VerboseNestedListSerializer(serializers.ListSerializer):
    """
    A special ListSerializer that preserves the verbose_field_name functionality
    for nested serializers with many=True.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract verbose_field_name if provided in kwargs
        self.verbose_field_name = kwargs.pop('verbose_field_name', None)
        super().__init__(*args, **kwargs)
    
    def to_representation(self, data):
        """
        List of objects -> List of dicts
        """
        # Standard implementation from DRF
        iterable = data.all() if hasattr(data, 'all') else data
        return [self.child.to_representation(item) for item in iterable]


# Extension of serializer fields to support verbose_field_name

def add_verbose_field_name_to_field(field_class):
    """
    Function to extend a field class with verbose_field_name functionality.
    """
    original_init = field_class.__init__

    def new_init(self, *args, **kwargs):
        # Extract verbose_field_name if provided
        verbose_field_name = kwargs.pop('verbose_field_name', None)

        # Call the original __init__
        original_init(self, *args, **kwargs)

        # Set the verbose_field_name attribute
        self.verbose_field_name = verbose_field_name

    field_class.__init__ = new_init
    return field_class


# Apply the extension to all standard field types
VerboseCharField = add_verbose_field_name_to_field(serializers.CharField)
VerboseIntegerField = add_verbose_field_name_to_field(serializers.IntegerField)
VerboseBooleanField = add_verbose_field_name_to_field(serializers.BooleanField)
VerboseDateTimeField = add_verbose_field_name_to_field(serializers.DateTimeField)
VerboseDateField = add_verbose_field_name_to_field(serializers.DateField)
VerboseFloatField = add_verbose_field_name_to_field(serializers.FloatField)
VerboseDecimalField = add_verbose_field_name_to_field(serializers.DecimalField)
VerboseEmailField = add_verbose_field_name_to_field(serializers.EmailField)
VerboseSerializerMethodField = add_verbose_field_name_to_field(serializers.SerializerMethodField)
VerboseRelatedField = add_verbose_field_name_to_field(serializers.RelatedField)
VerbosePrimaryKeyRelatedField = add_verbose_field_name_to_field(serializers.PrimaryKeyRelatedField)
VerboseHyperlinkedRelatedField = add_verbose_field_name_to_field(serializers.HyperlinkedRelatedField)
VerboseSlugRelatedField = add_verbose_field_name_to_field(serializers.SlugRelatedField)
VerboseHyperlinkedIdentityField = add_verbose_field_name_to_field(serializers.HyperlinkedIdentityField)
VerboseListField = add_verbose_field_name_to_field(serializers.ListField)
VerboseDictField = add_verbose_field_name_to_field(serializers.DictField)
VerboseJSONField = add_verbose_field_name_to_field(serializers.JSONField)
VerboseStringRelatedField = add_verbose_field_name_to_field(serializers.StringRelatedField) 