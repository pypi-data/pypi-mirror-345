from malac.models.fhir import r4, r5, utils

__version__ = "1.1.0"

list_i_o_modules = {
    "http://hl7.org/fhir/4.0/StructureDefinition": r4,
    "http://hl7.org/fhir/4.3/StructureDefinition": r4,
    "http://hl7.org/fhir/5.0/StructureDefinition": r5,
    "http://hl7.org/fhir/StructureDefinition": r5,
}

for mod in [r4, r5]:
    mod.Resource.exportJsonAttributes = utils.exportJsonAttributesResource
    mod.ResourceContainer.exportJsonResult = utils.exportJsonResultResourceContainer
    mod.Narrative.exportJsonResult = utils.exportJsonResultNarrative
    mod.Element.exportJsonResult = utils.exportJsonResultElement
    mod.date.exportJsonAttributes = utils.exportJsonAttributesDateDateTime
    mod.dateTime.exportJsonAttributes = utils.exportJsonAttributesDateDateTime
