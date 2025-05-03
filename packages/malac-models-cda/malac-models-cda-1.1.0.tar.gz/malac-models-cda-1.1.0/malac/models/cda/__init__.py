from malac.models.cda import at_ext, ch_ext_pharm, it_ext

__version__ = "1.1.0"

list_i_o_modules = {
    "http://hl7.org/fhir/cda/StructureDefinition": {
        None: at_ext, 
        "AT": at_ext,
        "CH": ch_ext_pharm,
        "IT": it_ext,
    },
    "http://hl7.org/cda/stds/core/StructureDefinition": {
        None: at_ext, 
        "AT": at_ext,
        "CH": ch_ext_pharm,
        "IT": it_ext,
    },
}

at_ext.AD.choice_group_names = ["item"]
at_ext.EN.choice_group_names = ["item"]
at_ext.ON.choice_group_names = ["item"]
ch_ext_pharm.AD.choice_group_names = ["item"]
ch_ext_pharm.EN.choice_group_names = ["item"]
ch_ext_pharm.ON.choice_group_names = ["item"]
