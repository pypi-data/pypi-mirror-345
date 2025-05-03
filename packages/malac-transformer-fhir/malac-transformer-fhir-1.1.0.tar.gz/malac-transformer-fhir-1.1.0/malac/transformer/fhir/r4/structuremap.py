
import sys
import argparse
import time
import uuid
import builtins
import re
import io
import json
from datetime import datetime
import dateutil.parser
from html import escape as html_escape
import malac.models.fhir.r4
import malac.models.fhir.r5
from malac.models.fhir.r5 import string, base64Binary, markdown, code, dateTime, uri, boolean, decimal
from malac.models.fhir import utils
from malac.utils import fhirpath

description_text = "This has been compiled by the MApping LAnguage compiler for Health Data, short MaLaC-HD. See arguments for more details."
one_timestamp = datetime.now()
fhirpath_utils = fhirpath.FHIRPathUtils(malac.models.fhir.r5)
shared_vars = {}

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument(
       '-s', '--source', help='the source file path', required=True
    )
    parser.add_argument(
       '-t', '--target', help='the target file path the result will be written to', required=True
    )
    return parser

def transform(source_path, target_path):
    start = time.time()
    print('+++++++ Transformation from '+source_path+' to '+target_path+' started +++++++')

    if source_path.endswith('.xml'):
        src = malac.models.fhir.r4.parse(source_path, silence=True)
    elif source_path.endswith('.json'):
        with open(source_path, 'r', newline='', encoding='utf-8') as f:
            src = utils.parse_json(malac.models.fhir.r4, json.load(f))
    else:
        raise BaseException('Unknown source file ending: ' + source_path)
    tgt = malac.models.fhir.r5.StructureMap()
    StructureMap(src, tgt)
    with open(target_path, 'w', newline='', encoding='utf-8') as f:
        if target_path.endswith('.xml'):
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            tgt.export(f, 0, namespacedef_='xmlns="http://hl7.org/fhir" xmlns:v3="urn:hl7-org:v3"')
        elif target_path.endswith('.json'):
            json.dump(tgt.exportJson(), f)
        else:
            raise BaseException('Unknown target file ending')

    print('altogether in '+str(round(time.time()-start,3))+' seconds.')
    print('+++++++ Transformation from '+source_path+' to '+target_path+' ended  +++++++')

def StructureMap(src, tgt):
    DomainResource(src, tgt)
    if src.url:
        tgt.url = malac.models.fhir.r5.uri()
        transform_default(src.url, tgt.url)
    for identifier in src.identifier or []:
        tgt.identifier.append(malac.models.fhir.r5.Identifier())
        transform_default(identifier, tgt.identifier[-1])
    if src.version:
        tgt.version = malac.models.fhir.r5.string()
        transform_default(src.version, tgt.version)
    if src.name:
        tgt.name = malac.models.fhir.r5.string()
        transform_default(src.name, tgt.name)
    if src.title:
        tgt.title = malac.models.fhir.r5.string()
        transform_default(src.title, tgt.title)
    v = src.status
    if v:
        match = translate_single('PublicationStatus', (v if isinstance(v, str) else v.value), 'code')
        tgt.status = string(value=match)
    if src.experimental:
        tgt.experimental = malac.models.fhir.r5.boolean()
        transform_default(src.experimental, tgt.experimental)
    if src.date:
        tgt.date = malac.models.fhir.r5.dateTime()
        transform_default(src.date, tgt.date)
    if src.publisher:
        tgt.publisher = malac.models.fhir.r5.string()
        transform_default(src.publisher, tgt.publisher)
    for contact in src.contact or []:
        tgt.contact.append(malac.models.fhir.r5.ContactDetail())
        transform_default(contact, tgt.contact[-1])
    if src.description:
        tgt.description = malac.models.fhir.r5.markdown()
        transform_default(src.description, tgt.description)
    for useContext in src.useContext or []:
        tgt.useContext.append(malac.models.fhir.r5.UsageContext())
        transform_default(useContext, tgt.useContext[-1])
    for jurisdiction in src.jurisdiction or []:
        tgt.jurisdiction.append(malac.models.fhir.r5.CodeableConcept())
        transform_default(jurisdiction, tgt.jurisdiction[-1])
    if src.purpose:
        tgt.purpose = malac.models.fhir.r5.markdown()
        transform_default(src.purpose, tgt.purpose)
    if src.copyright:
        tgt.copyright = malac.models.fhir.r5.markdown()
        transform_default(src.copyright, tgt.copyright)
    for s in src.structure or []:
        t = malac.models.fhir.r5.StructureMap_Structure()
        tgt.structure.append(t)
        StructureMapStructure(s, t)
    for import_ in src.import_ or []:
        tgt.import_.append(malac.models.fhir.r5.canonical())
        transform_default(import_, tgt.import_[-1])
    for s in src.group or []:
        t = malac.models.fhir.r5.StructureMap_Group()
        tgt.group.append(t)
        StructureMapGroup(s, t)

def StructureMapStructure(src, tgt):
    BackboneElement(src, tgt)
    if src.url:
        tgt.url = malac.models.fhir.r5.canonical()
        transform_default(src.url, tgt.url)
    v = src.mode
    if v:
        match = translate_single('StructureMapModelMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.mode = string(value=match)
    if src.alias:
        tgt.alias = malac.models.fhir.r5.string()
        transform_default(src.alias, tgt.alias)
    if src.documentation:
        tgt.documentation = malac.models.fhir.r5.string()
        transform_default(src.documentation, tgt.documentation)

def StructureMapGroup(src, tgt):
    BackboneElement(src, tgt)
    if src.name:
        tgt.name = malac.models.fhir.r5.id()
        transform_default(src.name, tgt.name)
    if src.extends:
        tgt.extends = malac.models.fhir.r5.id()
        transform_default(src.extends, tgt.extends)
    v = src.typeMode
    if v:
        match = translate_single('StructureMapGroupTypeMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.typeMode = string(value=match)
    if src.documentation:
        tgt.documentation = malac.models.fhir.r5.string()
        transform_default(src.documentation, tgt.documentation)
    for s in src.input or []:
        t = malac.models.fhir.r5.StructureMap_Input()
        tgt.input.append(t)
        StructureMapGroupInput(s, t)
    for s in src.rule or []:
        t = malac.models.fhir.r5.StructureMap_Rule()
        tgt.rule.append(t)
        StructureMapGroupRule(s, t)

def StructureMapGroupInput(src, tgt):
    BackboneElement(src, tgt)
    if src.name:
        tgt.name = malac.models.fhir.r5.id()
        transform_default(src.name, tgt.name)
    if src.type_:
        tgt.type_ = malac.models.fhir.r5.string()
        transform_default(src.type_, tgt.type_)
    v = src.mode
    if v:
        match = translate_single('StructureMapInputMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.mode = string(value=match)
    if src.documentation:
        tgt.documentation = malac.models.fhir.r5.string()
        transform_default(src.documentation, tgt.documentation)

def StructureMapGroupRule(src, tgt):
    BackboneElement(src, tgt)
    if src.name:
        tgt.name = malac.models.fhir.r5.id()
        transform_default(src.name, tgt.name)
    for s in src.source or []:
        t = malac.models.fhir.r5.StructureMap_Source()
        tgt.source.append(t)
        StructureMapGroupRuleSource(s, t)
    for s in src.target or []:
        t = malac.models.fhir.r5.StructureMap_Target()
        tgt.target.append(t)
        StructureMapGroupRuleTarget(s, t)
    for s in src.rule or []:
        t = malac.models.fhir.r5.StructureMap_Rule()
        tgt.rule.append(t)
        StructureMapGroupRule(s, t)
    for s in src.dependent or []:
        t = malac.models.fhir.r5.StructureMap_Dependent()
        tgt.dependent.append(t)
        StructureMapGroupRuleDependent(s, t)
    if src.documentation:
        tgt.documentation = malac.models.fhir.r5.string()
        transform_default(src.documentation, tgt.documentation)

def StructureMapGroupRuleSource(src, tgt):
    BackboneElement(src, tgt)
    if src.context:
        tgt.context = malac.models.fhir.r5.id()
        transform_default(src.context, tgt.context)
    if src.min:
        tgt.min = malac.models.fhir.r5.integer()
        transform_default(src.min, tgt.min)
    if src.max:
        tgt.max = malac.models.fhir.r5.string()
        transform_default(src.max, tgt.max)
    if src.type_:
        tgt.type_ = malac.models.fhir.r5.string()
        transform_default(src.type_, tgt.type_)
    for defaultValue in (src.defaultValueString if isinstance(src.defaultValueString, list) else ([] if not src.defaultValueString else [src.defaultValueString])):
        if isinstance(defaultValue, malac.models.fhir.r4.string):
            tgt.defaultValue = malac.models.fhir.r5.string()
            transform_default(defaultValue, tgt.defaultValue)
    if src.element:
        tgt.element = malac.models.fhir.r5.string()
        transform_default(src.element, tgt.element)
    v = src.listMode
    if v:
        match = translate_single('StructureMapSourceListMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.listMode = string(value=match)
    if src.variable:
        tgt.variable = malac.models.fhir.r5.id()
        transform_default(src.variable, tgt.variable)
    if src.condition:
        tgt.condition = malac.models.fhir.r5.string()
        transform_default(src.condition, tgt.condition)
    if src.check:
        tgt.check = malac.models.fhir.r5.string()
        transform_default(src.check, tgt.check)
    if src.logMessage:
        tgt.logMessage = malac.models.fhir.r5.string()
        transform_default(src.logMessage, tgt.logMessage)

def StructureMapGroupRuleTarget(src, tgt):
    BackboneElement(src, tgt)
    if src.context:
        tgt.context = malac.models.fhir.r5.string()
        transform_default(src.context, tgt.context)
    if src.element:
        tgt.element = malac.models.fhir.r5.string()
        transform_default(src.element, tgt.element)
    if src.variable:
        tgt.variable = malac.models.fhir.r5.id()
        transform_default(src.variable, tgt.variable)
    for v in src.listMode or []:
        match = translate_single('StructureMapTargetListMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.listMode.append(string(value=match))
    if src.listRuleId:
        tgt.listRuleId = malac.models.fhir.r5.id()
        transform_default(src.listRuleId, tgt.listRuleId)
    v = src.transform
    if v:
        match = translate_single('StructureMapTransform', (v if isinstance(v, str) else v.value), 'code')
        tgt.transform = string(value=match)
    for s in src.parameter or []:
        t = malac.models.fhir.r5.StructureMap_Parameter()
        tgt.parameter.append(t)
        StructureMapGroupRuleTargetParameter(s, t)

def StructureMapGroupRuleTargetParameter(src, tgt):
    BackboneElement(src, tgt)
    for value in (src.valueId if isinstance(src.valueId, list) else ([] if not src.valueId else [src.valueId])):
        if isinstance(value, malac.models.fhir.r4.id):
            tgt.valueId = malac.models.fhir.r5.id()
            transform_default(value, tgt.valueId)
    for value_ in (src.valueString if isinstance(src.valueString, list) else ([] if not src.valueString else [src.valueString])):
        if isinstance(value_, malac.models.fhir.r4.string):
            tgt.valueString = malac.models.fhir.r5.string()
            transform_default(value_, tgt.valueString)
    for value__ in (src.valueBoolean if isinstance(src.valueBoolean, list) else ([] if not src.valueBoolean else [src.valueBoolean])):
        if isinstance(value__, malac.models.fhir.r4.boolean):
            tgt.valueBoolean = malac.models.fhir.r5.boolean()
            transform_default(value__, tgt.valueBoolean)
    for value___ in (src.valueInteger if isinstance(src.valueInteger, list) else ([] if not src.valueInteger else [src.valueInteger])):
        if isinstance(value___, malac.models.fhir.r4.integer):
            tgt.valueInteger = malac.models.fhir.r5.integer()
            transform_default(value___, tgt.valueInteger)
    for value____ in (src.valueDecimal if isinstance(src.valueDecimal, list) else ([] if not src.valueDecimal else [src.valueDecimal])):
        if isinstance(value____, malac.models.fhir.r4.decimal):
            tgt.valueDecimal = malac.models.fhir.r5.decimal()
            transform_default(value____, tgt.valueDecimal)

def StructureMapGroupRuleDependent(src, tgt):
    BackboneElement(src, tgt)
    if src.name:
        tgt.name = malac.models.fhir.r5.id()
        transform_default(src.name, tgt.name)
    for v in src.variable or []:
        p = malac.models.fhir.r5.StructureMap_Parameter()
        tgt.parameter.append(p)
        p.valueString = v

# output
# 1..1 result (boolean)
# 0..1 message with error details for human (string)
# 0..* match with (list)
#   0..1 equivalnce (string from https://hl7.org/fhir/R4B/valueset-concept-map-equivalence.html)
#   0..1 concept
#       0..1 system
#       0..1 version
#       0..1 code
#       0..1 display 
#       0..1 userSelected will always be false, because this is a translation
#   0..1 source (conceptMap url)
# TODO implement reverse
def translate(url=None, conceptMapVersion=None, code=None, system=None, version=None, source=None, coding=None, codeableConcept=None, target=None, targetsystem=None, reverse=None, silent=False)              -> dict [bool, str, list[dict[str, dict[str, str, str, str, bool], str]]]:
    start = time.time()
    
    # start validation and recall of translate in simple from
    if codeableConcept:
        if isinstance(codeableConcept, str): 
            codeableConcept = malac.models.fhir.r4.parseString(codeableConcept, silent)
        elif isinstance(coding, malac.models.fhir.r4.CodeableConcept):
            pass
        else:
            sys.exit("The codeableConcept parameter has to be a string or a CodeableConcept Object (called method as library)!")
        # the first fit will be returned, else the last unfitted value will be returned
        # TODO check translate params
        for one_coding in codeableConcept.get_coding:
            if (ret := translate(url=url, source=source, coding=one_coding, 
                                 target=target, targetsystem=targetsystem, 
                                 reverse=reverse, silent=True))[0]:
                return ret
        else: return ret
    elif coding:
        if isinstance(coding, str): 
            coding = malac.models.fhir.r4.parseString(coding, silent)
        elif isinstance(coding, malac.models.fhir.r4.Coding):
            pass
        else:
            sys.exit("The coding parameter has to be a string or a Coding Object (called method as library)!")
        # TODO check translate params
        return translate(url=url,  source=source, coding=one_coding, 
                         target=target, targetsystem=targetsystem, 
                         reverse=reverse, silent=True)
    elif code:
        if not isinstance(code,str): 
            sys.exit("The code parameter has to be a string!")
    elif target:
        if not isinstance(code,str): 
            sys.exit("The target parameter has to be a string!")
    elif targetsystem:
        if not isinstance(code,str): 
            sys.exit("The targetsystem parameter has to be a string!")
    else:
        sys.exit("At least codeableConcept, coding, code, target or targetSystem has to be given!")
    # end validation and recall of translate in simplier from

    # look for any information from the one ore more generated conceptMaps into con_map_7d
    match = []
    unmapped = []
    if url not in con_map_7d.keys():
        print('   #ERROR# ConceptMap with URL "'+ url +'" is not loaded to this compiled conceptMap #ERROR#')
    else:
        for url_lvl in con_map_7d:
            if url_lvl == "%" or url_lvl == str(url or ""):#+str(("/?version=" and conceptMapVersion) or ""):
                for source_lvl in con_map_7d[url_lvl]:
                    if source_lvl == "%" or not source or source_lvl == source:
                        for target_lvl in con_map_7d[url_lvl][source_lvl]:
                            if target_lvl == "%" or not target or target_lvl == target:
                                for system_lvl in con_map_7d[url_lvl][source_lvl][target_lvl]:
                                    if system_lvl == "%" or not system or system_lvl == system:#+str(("/?version=" and version) or ""):
                                        for targetsystem_lvl in con_map_7d[url_lvl][source_lvl][target_lvl][system_lvl]:
                                            if targetsystem_lvl == "%" or not targetsystem or targetsystem_lvl == targetsystem:
                                                for code_lvl in con_map_7d[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl]:
                                                    if code_lvl == "|" or code_lvl == "~" or code_lvl == "#":
                                                        unmapped += con_map_7d[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl][code_lvl]
                                                    if code_lvl == "%" or not code or code_lvl == code:
                                                        match += con_map_7d[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl][code_lvl]                
                                                    
    if not match:
        for one_unmapped in unmapped:
            tmp_system = ""
            tmp_version = ""
            tmp_code = ""
            tmp_display = ""
            # replace all "|" values with to translated code (provided from https://hl7.org/fhir/R4B/conceptmap-definitions.html#ConceptMap.group.unmapped.mode)
            if one_unmapped["concept"]["code"].startswith("|"):
                tmp_system = system
                tmp_version = version
                tmp_code = one_unmapped["concept"]["code"][1:] + code
            # replace all "~" values with fixed code (provided from https://hl7.org/fhir/R4B/conceptmap-definitions.html#ConceptMap.group.unmapped.mode)
            elif one_unmapped["concept"]["code"].startswith("~"):
                tmp_code = one_unmapped["concept"]["code"][1:]
                tmp_display = one_unmapped["concept"]["display"]
            elif one_unmapped["concept"]["code"].startswith("#"):
                # TODO detect recursion like conceptMapA -> conceptMapB -> ConceptMapA -> ...
                return translate(one_unmapped["concept"]["code"][1:], None, code, system, version, source, 
                                 coding, codeableConcept, target, targetsystem, reverse, silent)
            match.append({"equivalence": one_unmapped["equivalence"], 
                          "concept":{
                            "system": tmp_system, 
                            "version": tmp_version, # TODO version of codesystem out of url?
                            "code": tmp_code,
                            "display": tmp_display,
                            "userSelected": False},
                          "source": one_unmapped["source"]})

    # see if any match is not "unmatched" or "disjoint"
    result = False
    message = ""
    for one_match in match:
        if one_match["equivalence"] != "unmatched" and one_match["equivalence"] != "disjoint":
            result = True 

    if not silent:
        print('Translation in '+str(round(time.time()-start,3))+' seconds for code "'+code+'" with ConceptMap "'+url+'"')
    return {"result": result, "message": message, "match": match}

# The con_map_7d is a seven dimensional dictionary, for quickly finding the fitting translation
# All dimensions except the last are optional, so a explicit NONE value will be used as key and 
# interpreted as the default key, that always will be fitting, no matter what other keys are fitting.
# If a version is included (purely optional), than the version will be added with a blank before to the key
#
# The 0th dimension is mandatory and stating the ConceptMap with its url (including the version).
#
# The 1st dimension is optional and stating the SOURCE valueset (including the version), as one conceptMap can only 
# have a maximum of one SOURCE, this is reserved for MaLaC-HD ability to process multiple ConceptMaps in one output.
#
# The 2nd dimension is optional and stating the TARGET valueset (including the version), as one conceptMap can only 
# have a maximum of one TARGET, this is reserved for MaLaC-HD ability to process multiple ConceptMaps in one output.
#
# The 3th dimension is optional and stating the SYSTEM (including the version) from the source valueset code, as one 
# code could be used in multiple SYSTEMs from the source valueset to translate. 
# Not stating a SYSTEM with a code, is not FHIR compliant and not a whole concept, but still a valid conceptmap.
# As many conceptMaps exists that are worngly using this SYSTEM element as stating the valueset, that should be
# stated in source, this case will still be supported by MaLaC-HD. Having a conceptMap with a source valueset 
# and a different SYSTEM valueset will result in an impossible match and an error will not be recognized by MaLaC-HD.
#
# The 4th dimension is optional and stating the TARGET SYSTEM (including the version) from the target valueset code, as one 
# code could be used in multiple SYSTEMs from the target valueset to translate. 
# Not stating a TARGET SYSTEM with a code, is not FHIR compliant and not a whole concept, but still a valid conceptmap.
# As many conceptMaps exists that are worngly using this TARGET SYSTEM element as stating the target valueset, that should be
# stated in target, this case will still be supported by MaLaC-HD. Having a conceptMap with a target valueset 
# and a different TARGET SYSTEM valueset will result in an impossible match and an error will not be recognized by MaLaC-HD.
#   
# The 5th dimension is optional and stating the CODE from the source valueset, as one conceptMap can have none or 
# multiple CODEs from the source to translate. 
#
# The 6th dimension is NOT optional and stating the TARGET CODE from the target valueset. As one source code could be translated 
# in multiple TARGET CODEs, the whole set have to be returend. 
# For a translation with explicitly no TARGET CODE, because of an quivalence of unmatched or disjoint, NONE will be returned. 
#   
# a minimal example, translating "hi" to "servus": 
# con_map_7d = {"myConMap": {None: {None: {"hi": {None: {None: ["equivalent", "<coding><code>servus</code></coding>", "https://my.concept.map/conceptMap/my"]}}}}}
#
# TODO add a dimension for a specific dependsOn property
# TODO add a solution for the unmapped element
con_map_7d = {}


con_map_7d["PublicationStatus"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/publication-status": {
                "http://hl7.org/fhir/publication-status": {
                    "draft": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "draft",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "active": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "active",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "retired": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "retired",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "unknown": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "unknown",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapGroupTypeMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-group-type-mode": {
                "http://hl7.org/fhir/map-group-type-mode": {
                    "types": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-group-type-mode",
                                "version": "",
                                "code": "types",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapGroupTypeMode"
                        }
                    ],
                    "type-and-types": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-group-type-mode",
                                "version": "",
                                "code": "type-and-types",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapGroupTypeMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapInputMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-input-mode": {
                "http://hl7.org/fhir/map-input-mode": {
                    "source": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-input-mode",
                                "version": "",
                                "code": "source",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapInputMode"
                        }
                    ],
                    "target": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-input-mode",
                                "version": "",
                                "code": "target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapInputMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapModelMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-model-mode": {
                "http://hl7.org/fhir/map-model-mode": {
                    "source": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-model-mode",
                                "version": "",
                                "code": "source",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapModelMode"
                        }
                    ],
                    "queried": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-model-mode",
                                "version": "",
                                "code": "queried",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapModelMode"
                        }
                    ],
                    "target": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-model-mode",
                                "version": "",
                                "code": "target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapModelMode"
                        }
                    ],
                    "produced": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-model-mode",
                                "version": "",
                                "code": "produced",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapModelMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapSourceListMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-source-list-mode": {
                "http://hl7.org/fhir/map-source-list-mode": {
                    "first": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-source-list-mode",
                                "version": "",
                                "code": "first",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapSourceListMode"
                        }
                    ],
                    "not_first": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-source-list-mode",
                                "version": "",
                                "code": "not_first",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapSourceListMode"
                        }
                    ],
                    "last": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-source-list-mode",
                                "version": "",
                                "code": "last",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapSourceListMode"
                        }
                    ],
                    "not_last": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-source-list-mode",
                                "version": "",
                                "code": "not_last",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapSourceListMode"
                        }
                    ],
                    "only_one": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-source-list-mode",
                                "version": "",
                                "code": "only_one",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapSourceListMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapTargetListMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-target-list-mode": {
                "http://hl7.org/fhir/map-target-list-mode": {
                    "first": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-target-list-mode",
                                "version": "",
                                "code": "first",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTargetListMode"
                        }
                    ],
                    "share": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-target-list-mode",
                                "version": "",
                                "code": "share",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTargetListMode"
                        }
                    ],
                    "last": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-target-list-mode",
                                "version": "",
                                "code": "last",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTargetListMode"
                        }
                    ],
                    "collate": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-target-list-mode",
                                "version": "",
                                "code": "single",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTargetListMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["StructureMapTransform"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/map-transform": {
                "http://hl7.org/fhir/map-transform": {
                    "create": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "create",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "copy": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "copy",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "truncate": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "truncate",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "escape": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "escape",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "cast": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "cast",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "append": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "append",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "translate": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "translate",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "reference": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "reference",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "dateOp": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "dateOp",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "uuid": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "uuid",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "pointer": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "pointer",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "evaluate": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "evaluate",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "cc": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "cc",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "c": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "c",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "qty": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "qty",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "id": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "id",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ],
                    "cp": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/map-transform",
                                "version": "",
                                "code": "cp",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "StructureMapTransform"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["ConceptMapGroupUnmappedMode"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/conceptmap-unmapped-mode": {
                "http://hl7.org/fhir/conceptmap-unmapped-mode": {
                    "provided": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/conceptmap-unmapped-mode",
                                "version": "",
                                "code": "use-source-code",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapGroupUnmappedMode"
                        }
                    ],
                    "fixed": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/conceptmap-unmapped-mode",
                                "version": "",
                                "code": "fixed",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapGroupUnmappedMode"
                        }
                    ],
                    "other-map": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/conceptmap-unmapped-mode",
                                "version": "",
                                "code": "other-map",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapGroupUnmappedMode"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["ConceptMapRelationship"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/concept-map-equivalence": {
                "http://hl7.org/fhir/concept-map-relationship": {
                    "relatedto": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "related-to",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "inexact": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "related-to",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "equivalent": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "equivalent",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "equal": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "equivalent",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "wider": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "source-is-narrower-than-target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "subsumes": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "source-is-narrower-than-target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "narrower": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "source-is-broader-than-target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "specializes": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "source-is-broader-than-target",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "unmatched": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "not-related-to",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ],
                    "disjoint": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/concept-map-equivalence",
                                "version": "",
                                "code": "not-related-to",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "ConceptMapRelationship"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["PublicationStatus"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/publication-status": {
                "http://hl7.org/fhir/publication-status": {
                    "draft": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "draft",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "active": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "active",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "retired": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "retired",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ],
                    "unknown": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/publication-status",
                                "version": "",
                                "code": "unknown",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "PublicationStatus"
                        }
                    ]
                }
            }
        }
    }
}

con_map_7d["NarrativeStatus"] = {
    "%": {
        "%": {
            "http://hl7.org/fhir/4.3/narrative-status": {
                "http://hl7.org/fhir/narrative-status": {
                    "generated": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/narrative-status",
                                "version": "",
                                "code": "generated",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "NarrativeStatus"
                        }
                    ],
                    "extensions": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/narrative-status",
                                "version": "",
                                "code": "extensions",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "NarrativeStatus"
                        }
                    ],
                    "additional": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/narrative-status",
                                "version": "",
                                "code": "additional",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "NarrativeStatus"
                        }
                    ],
                    "empty": [
                        {
                            "equivalence": "equivalent",
                            "concept": {
                                "system": "http://hl7.org/fhir/4.3/narrative-status",
                                "version": "",
                                "code": "empty",
                                "display": "",
                                "userSelected": False
                            },
                            "source": "NarrativeStatus"
                        }
                    ]
                }
            }
        }
    }
}
def ConceptMap(src, tgt):
    DomainResource(src, tgt)
    if src.url:
        tgt.url = malac.models.fhir.r5.uri()
        transform_default(src.url, tgt.url)
    if src.identifier:
        tgt.identifier.append(malac.models.fhir.r5.Identifier())
        transform_default(src.identifier, tgt.identifier[-1])
    if src.version:
        tgt.version = malac.models.fhir.r5.string()
        transform_default(src.version, tgt.version)
    if src.name:
        tgt.name = malac.models.fhir.r5.string()
        transform_default(src.name, tgt.name)
    if src.title:
        tgt.title = malac.models.fhir.r5.string()
        transform_default(src.title, tgt.title)
    v = src.status
    if v:
        match = translate_single('PublicationStatus', (v if isinstance(v, str) else v.value), 'code')
        tgt.status = string(value=match)
    if src.experimental:
        tgt.experimental = malac.models.fhir.r5.boolean()
        transform_default(src.experimental, tgt.experimental)
    if src.date:
        tgt.date = malac.models.fhir.r5.dateTime()
        transform_default(src.date, tgt.date)
    if src.publisher:
        tgt.publisher = malac.models.fhir.r5.string()
        transform_default(src.publisher, tgt.publisher)
    for contact in src.contact or []:
        tgt.contact.append(malac.models.fhir.r5.ContactDetail())
        transform_default(contact, tgt.contact[-1])
    if src.description:
        tgt.description = malac.models.fhir.r5.markdown()
        transform_default(src.description, tgt.description)
    for useContext in src.useContext or []:
        tgt.useContext.append(malac.models.fhir.r5.UsageContext())
        transform_default(useContext, tgt.useContext[-1])
    for jurisdiction in src.jurisdiction or []:
        tgt.jurisdiction.append(malac.models.fhir.r5.CodeableConcept())
        transform_default(jurisdiction, tgt.jurisdiction[-1])
    if src.purpose:
        tgt.purpose = malac.models.fhir.r5.markdown()
        transform_default(src.purpose, tgt.purpose)
    if src.copyright:
        tgt.copyright = malac.models.fhir.r5.markdown()
        transform_default(src.copyright, tgt.copyright)
    for source in (src.sourceUri if isinstance(src.sourceUri, list) else ([] if not src.sourceUri else [src.sourceUri])):
        if isinstance(source, malac.models.fhir.r4.uri):
            tgt.sourceScopeUri = malac.models.fhir.r5.uri()
            transform_default(source, tgt.sourceScopeUri)
    for source_ in (src.sourceCanonical if isinstance(src.sourceCanonical, list) else ([] if not src.sourceCanonical else [src.sourceCanonical])):
        if isinstance(source_, malac.models.fhir.r4.canonical):
            tgt.sourceScopeCanonical = malac.models.fhir.r5.canonical()
            transform_default(source_, tgt.sourceScopeCanonical)
    for target in (src.targetUri if isinstance(src.targetUri, list) else ([] if not src.targetUri else [src.targetUri])):
        if isinstance(target, malac.models.fhir.r4.uri):
            tgt.targetScopeUri = malac.models.fhir.r5.uri()
            transform_default(target, tgt.targetScopeUri)
    for target_ in (src.targetCanonical if isinstance(src.targetCanonical, list) else ([] if not src.targetCanonical else [src.targetCanonical])):
        if isinstance(target_, malac.models.fhir.r4.canonical):
            tgt.targetScopeCanonical = malac.models.fhir.r5.canonical()
            transform_default(target_, tgt.targetScopeCanonical)
    for s in src.group or []:
        t = malac.models.fhir.r5.ConceptMap_Group()
        tgt.group.append(t)
        ConceptMapGroup(s, t)

def ConceptMapGroup(src, tgt):
    BackboneElement(src, tgt)
    if src.source:
        tgt.source = malac.models.fhir.r5.canonical()
        transform_default(src.source, tgt.source)
    if src.target:
        tgt.target = malac.models.fhir.r5.canonical()
        transform_default(src.target, tgt.target)
    for s in src.element or []:
        t = malac.models.fhir.r5.ConceptMap_Element()
        tgt.element.append(t)
        ConceptMapGroupElement(s, t)
    s = src.unmapped
    if s:
        t = malac.models.fhir.r5.ConceptMap_Unmapped()
        if tgt.unmapped is not None:
            t = tgt.unmapped
        else:
            tgt.unmapped = t
        ConceptMapGroupUnmapped(s, t)

def ConceptMapGroupElement(src, tgt):
    BackboneElement(src, tgt)
    if src.code:
        tgt.code = malac.models.fhir.r5.code()
        transform_default(src.code, tgt.code)
    if src.display:
        tgt.display = malac.models.fhir.r5.string()
        transform_default(src.display, tgt.display)
    if fhirpath.single([all(fhirpath_utils.equals(fhirpath_utils.get(v3,'equivalence'), '==', ['unmatched']) == [True] for v3 in [v2 for v1 in [src] for v2 in fhirpath_utils.get(v1,'target')])]):
        t = malac.models.fhir.r5.boolean()
        if tgt.noMap is not None:
            t = tgt.noMap
        else:
            tgt.noMap = t
        t.value = True
    for s in src.target or []:
        if fhirpath.single(fhirpath_utils.equals([s], '!=', ['unmatched'])):
            t = malac.models.fhir.r5.ConceptMap_Target()
            tgt.target.append(t)
            ConceptMapGroupElementTarget(s, t)

def ConceptMapGroupElementTarget(src, tgt):
    BackboneElement(src, tgt)
    if src.code:
        tgt.code = malac.models.fhir.r5.code()
        transform_default(src.code, tgt.code)
    if src.display:
        tgt.display = malac.models.fhir.r5.string()
        transform_default(src.display, tgt.display)
    v = src.equivalence
    if v:
        match = translate_single('ConceptMapRelationship', (v if isinstance(v, str) else v.value), 'code')
        tgt.relationship = string(value=match)
    if src.comment:
        tgt.comment = malac.models.fhir.r5.string()
        transform_default(src.comment, tgt.comment)
    for s in src.dependsOn or []:
        t = malac.models.fhir.r5.ConceptMap_DependsOn()
        tgt.dependsOn.append(t)
        ConceptMapGroupElementTargetDependsOn(s, t)
    for s in src.product or []:
        t = malac.models.fhir.r5.ConceptMap_DependsOn()
        tgt.product.append(t)
        ConceptMapGroupElementTargetDependsOn(s, t)

def ConceptMapGroupElementTargetDependsOn(src, tgt):
    BackboneElement(src, tgt)
    if src.property:
        tgt.attribute = malac.models.fhir.r5.code()
        transform_default(src.property, tgt.attribute)
    if src.value:
        if fhirpath.single([not([v2 for v1 in [src] for v2 in fhirpath_utils.get(v1,'system')])]):
            transform_default(src.value, tgt.value)
    if fhirpath.single([bool([v2 for v1 in [src] for v2 in fhirpath_utils.get(v1,'system')])]):
        t = malac.models.fhir.r5.Coding()
        tgt.valueCoding = t
        if src.system:
            t.system = malac.models.fhir.r5.uri()
            transform_default(src.system, t.system)
        if src.value:
            t.code = malac.models.fhir.r5.code()
            transform_default(src.value, t.code)
        if src.display:
            t.display = malac.models.fhir.r5.string()
            transform_default(src.display, t.display)

def ConceptMapGroupUnmapped(src, tgt):
    BackboneElement(src, tgt)
    v = src.mode
    if v:
        match = translate_single('ConceptMapGroupUnmappedMode', (v if isinstance(v, str) else v.value), 'code')
        tgt.mode = string(value=match)
    if src.code:
        tgt.code = malac.models.fhir.r5.code()
        transform_default(src.code, tgt.code)
    if src.display:
        tgt.display = malac.models.fhir.r5.string()
        transform_default(src.display, tgt.display)
    if src.url:
        tgt.otherMap = malac.models.fhir.r5.canonical()
        transform_default(src.url, tgt.otherMap)

def DomainResource(src, tgt):
    Resource(src, tgt)
    if src.text:
        tgt.text = malac.models.fhir.r5.Narrative()
        transform_default(src.text, tgt.text)
    for contained in src.contained or []:
        if isinstance(contained, malac.models.fhir.r4.ResourceContainer):
            tgt.contained.append(malac.models.fhir.r5.ResourceContainer())
            transform_default(contained, tgt.contained[-1])
    for extension in src.extension or []:
        tgt.extension.append(malac.models.fhir.r5.Extension())
        transform_default(extension, tgt.extension[-1])
    for modifierExtension in src.modifierExtension or []:
        tgt.modifierExtension.append(malac.models.fhir.r5.Extension())
        transform_default(modifierExtension, tgt.modifierExtension[-1])

def Resource(src, tgt):
    Base(src)
    if src.id:
        tgt.id = malac.models.fhir.r5.id()
        StringToId(src.id, tgt.id)
    if src.meta:
        tgt.meta = malac.models.fhir.r5.Meta()
        transform_default(src.meta, tgt.meta)
    if src.implicitRules:
        tgt.implicitRules = malac.models.fhir.r5.uri()
        transform_default(src.implicitRules, tgt.implicitRules)
    if src.language:
        tgt.language = malac.models.fhir.r5.code()
        transform_default(src.language, tgt.language)

def Base(src):
    pass

def Element(src, tgt):
    if src.id:
        tgt.id = builtins.str()
        transform_default(src.id, tgt.id)
    for extension in src.extension or []:
        tgt.extension.append(malac.models.fhir.r5.Extension())
        transform_default(extension, tgt.extension[-1])

def BackboneElement(src, tgt):
    Element(src, tgt)
    for modifierExtension in src.modifierExtension or []:
        tgt.modifierExtension.append(malac.models.fhir.r5.Extension())
        transform_default(modifierExtension, tgt.modifierExtension[-1])

def Identifier(src, tgt):
    Element(src, tgt)
    if src.use:
        tgt.use = malac.models.fhir.r5.IdentifierUse()
        transform_default(src.use, tgt.use, malac.models.fhir.r5.code)
    if src.type_:
        tgt.type_ = malac.models.fhir.r5.CodeableConcept()
        transform_default(src.type_, tgt.type_)
    if src.system:
        tgt.system = malac.models.fhir.r5.uri()
        transform_default(src.system, tgt.system)
    if src.value:
        tgt.value = malac.models.fhir.r5.string()
        transform_default(src.value, tgt.value)
    if src.period:
        tgt.period = malac.models.fhir.r5.Period()
        transform_default(src.period, tgt.period)
    if src.assigner:
        tgt.assigner = malac.models.fhir.r5.Reference()
        transform_default(src.assigner, tgt.assigner)

def Meta(src, tgt):
    Element(src, tgt)
    if src.versionId:
        tgt.versionId = malac.models.fhir.r5.id()
        transform_default(src.versionId, tgt.versionId)
    if src.lastUpdated:
        tgt.lastUpdated = malac.models.fhir.r5.instant()
        transform_default(src.lastUpdated, tgt.lastUpdated)
    if src.source:
        tgt.source = malac.models.fhir.r5.uri()
        transform_default(src.source, tgt.source)
    for profile in src.profile or []:
        tgt.profile.append(malac.models.fhir.r5.canonical())
        transform_default(profile, tgt.profile[-1])
    for security in src.security or []:
        tgt.security.append(malac.models.fhir.r5.Coding())
        transform_default(security, tgt.security[-1])
    for tag in src.tag or []:
        tgt.tag.append(malac.models.fhir.r5.Coding())
        transform_default(tag, tgt.tag[-1])

def ContactDetail(src, tgt):
    Element(src, tgt)
    if src.name:
        tgt.name = malac.models.fhir.r5.string()
        transform_default(src.name, tgt.name)
    for telecom in src.telecom or []:
        tgt.telecom.append(malac.models.fhir.r5.ContactPoint())
        transform_default(telecom, tgt.telecom[-1])

def ContactPoint(src, tgt):
    Element(src, tgt)
    if src.system:
        tgt.system = malac.models.fhir.r5.ContactPointSystem()
        transform_default(src.system, tgt.system, malac.models.fhir.r5.code)
    if src.value:
        tgt.value = malac.models.fhir.r5.string()
        transform_default(src.value, tgt.value)
    if src.use:
        tgt.use = malac.models.fhir.r5.ContactPointUse()
        transform_default(src.use, tgt.use, malac.models.fhir.r5.code)
    if src.rank:
        tgt.rank = malac.models.fhir.r5.positiveInt()
        transform_default(src.rank, tgt.rank)
    if src.period:
        tgt.period = malac.models.fhir.r5.Period()
        transform_default(src.period, tgt.period)

def UsageContext(src, tgt):
    Element(src, tgt)
    if src.code:
        tgt.code = malac.models.fhir.r5.Coding()
        transform_default(src.code, tgt.code)
    for value in (src.valueCodeableConcept if isinstance(src.valueCodeableConcept, list) else ([] if not src.valueCodeableConcept else [src.valueCodeableConcept])):
        if isinstance(value, malac.models.fhir.r4.CodeableConcept):
            tgt.valueCodeableConcept = malac.models.fhir.r5.CodeableConcept()
            transform_default(value, tgt.valueCodeableConcept)
    for value_ in (src.valueQuantity if isinstance(src.valueQuantity, list) else ([] if not src.valueQuantity else [src.valueQuantity])):
        if isinstance(value_, malac.models.fhir.r4.Quantity):
            tgt.valueQuantity = malac.models.fhir.r5.Quantity()
            transform_default(value_, tgt.valueQuantity)
    for value__ in (src.valueRange if isinstance(src.valueRange, list) else ([] if not src.valueRange else [src.valueRange])):
        if isinstance(value__, malac.models.fhir.r4.Range):
            tgt.valueRange = malac.models.fhir.r5.Range()
            transform_default(value__, tgt.valueRange)
    for value___ in (src.valueReference if isinstance(src.valueReference, list) else ([] if not src.valueReference else [src.valueReference])):
        if isinstance(value___, malac.models.fhir.r4.Reference):
            tgt.valueReference = malac.models.fhir.r5.Reference()
            transform_default(value___, tgt.valueReference)

def Extension(src, tgt):
    Element(src, tgt)

def CodeableConcept(src, tgt):
    Element(src, tgt)
    for coding in src.coding or []:
        tgt.coding.append(malac.models.fhir.r5.Coding())
        transform_default(coding, tgt.coding[-1])
    if src.text:
        tgt.text = malac.models.fhir.r5.string()
        transform_default(src.text, tgt.text)

def Coding(src, tgt):
    Element(src, tgt)
    if src.system:
        tgt.system = malac.models.fhir.r5.uri()
        transform_default(src.system, tgt.system)
    if src.version:
        tgt.version = malac.models.fhir.r5.string()
        transform_default(src.version, tgt.version)
    if src.code:
        tgt.code = malac.models.fhir.r5.code()
        transform_default(src.code, tgt.code)
    if src.display:
        tgt.display = malac.models.fhir.r5.string()
        transform_default(src.display, tgt.display)
    if src.userSelected:
        tgt.userSelected = malac.models.fhir.r5.boolean()
        transform_default(src.userSelected, tgt.userSelected)

def ResourceContainer(src, tgt):
    if src.Account:
        tgt.Account = malac.models.fhir.r5.Account()
        transform_default(src.Account, tgt.Account)
    if src.ActivityDefinition:
        tgt.ActivityDefinition = malac.models.fhir.r5.ActivityDefinition()
        transform_default(src.ActivityDefinition, tgt.ActivityDefinition)
    if src.AdministrableProductDefinition:
        tgt.AdministrableProductDefinition = malac.models.fhir.r5.AdministrableProductDefinition()
        transform_default(src.AdministrableProductDefinition, tgt.AdministrableProductDefinition)
    if src.AdverseEvent:
        tgt.AdverseEvent = malac.models.fhir.r5.AdverseEvent()
        transform_default(src.AdverseEvent, tgt.AdverseEvent)
    if src.AllergyIntolerance:
        tgt.AllergyIntolerance = malac.models.fhir.r5.AllergyIntolerance()
        transform_default(src.AllergyIntolerance, tgt.AllergyIntolerance)
    if src.Appointment:
        tgt.Appointment = malac.models.fhir.r5.Appointment()
        transform_default(src.Appointment, tgt.Appointment)
    if src.AppointmentResponse:
        tgt.AppointmentResponse = malac.models.fhir.r5.AppointmentResponse()
        transform_default(src.AppointmentResponse, tgt.AppointmentResponse)
    if src.AuditEvent:
        tgt.AuditEvent = malac.models.fhir.r5.AuditEvent()
        transform_default(src.AuditEvent, tgt.AuditEvent)
    if src.Basic:
        tgt.Basic = malac.models.fhir.r5.Basic()
        transform_default(src.Basic, tgt.Basic)
    if src.Binary:
        tgt.Binary = malac.models.fhir.r5.Binary()
        transform_default(src.Binary, tgt.Binary)
    if src.BiologicallyDerivedProduct:
        tgt.BiologicallyDerivedProduct = malac.models.fhir.r5.BiologicallyDerivedProduct()
        transform_default(src.BiologicallyDerivedProduct, tgt.BiologicallyDerivedProduct)
    if src.BodyStructure:
        tgt.BodyStructure = malac.models.fhir.r5.BodyStructure()
        transform_default(src.BodyStructure, tgt.BodyStructure)
    if src.Bundle:
        tgt.Bundle = malac.models.fhir.r5.Bundle()
        transform_default(src.Bundle, tgt.Bundle)
    if src.CapabilityStatement:
        tgt.CapabilityStatement = malac.models.fhir.r5.CapabilityStatement()
        transform_default(src.CapabilityStatement, tgt.CapabilityStatement)
    if src.CarePlan:
        tgt.CarePlan = malac.models.fhir.r5.CarePlan()
        transform_default(src.CarePlan, tgt.CarePlan)
    if src.CareTeam:
        tgt.CareTeam = malac.models.fhir.r5.CareTeam()
        transform_default(src.CareTeam, tgt.CareTeam)
    if src.CatalogEntry:
        transform_default(src.CatalogEntry, tgt.CatalogEntry)
    if src.ChargeItem:
        tgt.ChargeItem = malac.models.fhir.r5.ChargeItem()
        transform_default(src.ChargeItem, tgt.ChargeItem)
    if src.ChargeItemDefinition:
        tgt.ChargeItemDefinition = malac.models.fhir.r5.ChargeItemDefinition()
        transform_default(src.ChargeItemDefinition, tgt.ChargeItemDefinition)
    if src.Citation:
        tgt.Citation = malac.models.fhir.r5.Citation()
        transform_default(src.Citation, tgt.Citation)
    if src.Claim:
        tgt.Claim = malac.models.fhir.r5.Claim()
        transform_default(src.Claim, tgt.Claim)
    if src.ClaimResponse:
        tgt.ClaimResponse = malac.models.fhir.r5.ClaimResponse()
        transform_default(src.ClaimResponse, tgt.ClaimResponse)
    if src.ClinicalImpression:
        tgt.ClinicalImpression = malac.models.fhir.r5.ClinicalImpression()
        transform_default(src.ClinicalImpression, tgt.ClinicalImpression)
    if src.ClinicalUseDefinition:
        tgt.ClinicalUseDefinition = malac.models.fhir.r5.ClinicalUseDefinition()
        transform_default(src.ClinicalUseDefinition, tgt.ClinicalUseDefinition)
    if src.CodeSystem:
        tgt.CodeSystem = malac.models.fhir.r5.CodeSystem()
        transform_default(src.CodeSystem, tgt.CodeSystem)
    if src.Communication:
        tgt.Communication = malac.models.fhir.r5.Communication()
        transform_default(src.Communication, tgt.Communication)
    if src.CommunicationRequest:
        tgt.CommunicationRequest = malac.models.fhir.r5.CommunicationRequest()
        transform_default(src.CommunicationRequest, tgt.CommunicationRequest)
    if src.CompartmentDefinition:
        tgt.CompartmentDefinition = malac.models.fhir.r5.CompartmentDefinition()
        transform_default(src.CompartmentDefinition, tgt.CompartmentDefinition)
    if src.Composition:
        tgt.Composition = malac.models.fhir.r5.Composition()
        transform_default(src.Composition, tgt.Composition)
    if src.ConceptMap:
        tgt.ConceptMap = (malac.models.fhir.r5.ConceptMap.subclass or malac.models.fhir.r5.ConceptMap)()
        transform_default(src.ConceptMap, tgt.ConceptMap)
    if src.Condition:
        tgt.Condition = malac.models.fhir.r5.Condition()
        transform_default(src.Condition, tgt.Condition)
    if src.Consent:
        tgt.Consent = malac.models.fhir.r5.Consent()
        transform_default(src.Consent, tgt.Consent)
    if src.Contract:
        tgt.Contract = malac.models.fhir.r5.Contract()
        transform_default(src.Contract, tgt.Contract)
    if src.Coverage:
        tgt.Coverage = malac.models.fhir.r5.Coverage()
        transform_default(src.Coverage, tgt.Coverage)
    if src.CoverageEligibilityRequest:
        tgt.CoverageEligibilityRequest = malac.models.fhir.r5.CoverageEligibilityRequest()
        transform_default(src.CoverageEligibilityRequest, tgt.CoverageEligibilityRequest)
    if src.CoverageEligibilityResponse:
        tgt.CoverageEligibilityResponse = malac.models.fhir.r5.CoverageEligibilityResponse()
        transform_default(src.CoverageEligibilityResponse, tgt.CoverageEligibilityResponse)
    if src.DetectedIssue:
        tgt.DetectedIssue = malac.models.fhir.r5.DetectedIssue()
        transform_default(src.DetectedIssue, tgt.DetectedIssue)
    if src.Device:
        tgt.Device = malac.models.fhir.r5.Device()
        transform_default(src.Device, tgt.Device)
    if src.DeviceDefinition:
        tgt.DeviceDefinition = malac.models.fhir.r5.DeviceDefinition()
        transform_default(src.DeviceDefinition, tgt.DeviceDefinition)
    if src.DeviceMetric:
        tgt.DeviceMetric = malac.models.fhir.r5.DeviceMetric()
        transform_default(src.DeviceMetric, tgt.DeviceMetric)
    if src.DeviceRequest:
        tgt.DeviceRequest = malac.models.fhir.r5.DeviceRequest()
        transform_default(src.DeviceRequest, tgt.DeviceRequest)
    if src.DeviceUseStatement:
        transform_default(src.DeviceUseStatement, tgt.DeviceUseStatement)
    if src.DiagnosticReport:
        tgt.DiagnosticReport = malac.models.fhir.r5.DiagnosticReport()
        transform_default(src.DiagnosticReport, tgt.DiagnosticReport)
    if src.DocumentManifest:
        transform_default(src.DocumentManifest, tgt.DocumentManifest)
    if src.DocumentReference:
        tgt.DocumentReference = malac.models.fhir.r5.DocumentReference()
        transform_default(src.DocumentReference, tgt.DocumentReference)
    if src.Encounter:
        tgt.Encounter = malac.models.fhir.r5.Encounter()
        transform_default(src.Encounter, tgt.Encounter)
    if src.Endpoint:
        tgt.Endpoint = malac.models.fhir.r5.Endpoint()
        transform_default(src.Endpoint, tgt.Endpoint)
    if src.EnrollmentRequest:
        tgt.EnrollmentRequest = malac.models.fhir.r5.EnrollmentRequest()
        transform_default(src.EnrollmentRequest, tgt.EnrollmentRequest)
    if src.EnrollmentResponse:
        tgt.EnrollmentResponse = malac.models.fhir.r5.EnrollmentResponse()
        transform_default(src.EnrollmentResponse, tgt.EnrollmentResponse)
    if src.EpisodeOfCare:
        tgt.EpisodeOfCare = malac.models.fhir.r5.EpisodeOfCare()
        transform_default(src.EpisodeOfCare, tgt.EpisodeOfCare)
    if src.EventDefinition:
        tgt.EventDefinition = malac.models.fhir.r5.EventDefinition()
        transform_default(src.EventDefinition, tgt.EventDefinition)
    if src.Evidence:
        tgt.Evidence = malac.models.fhir.r5.Evidence()
        transform_default(src.Evidence, tgt.Evidence)
    if src.EvidenceReport:
        tgt.EvidenceReport = malac.models.fhir.r5.EvidenceReport()
        transform_default(src.EvidenceReport, tgt.EvidenceReport)
    if src.EvidenceVariable:
        tgt.EvidenceVariable = malac.models.fhir.r5.EvidenceVariable()
        transform_default(src.EvidenceVariable, tgt.EvidenceVariable)
    if src.ExampleScenario:
        tgt.ExampleScenario = malac.models.fhir.r5.ExampleScenario()
        transform_default(src.ExampleScenario, tgt.ExampleScenario)
    if src.ExplanationOfBenefit:
        tgt.ExplanationOfBenefit = malac.models.fhir.r5.ExplanationOfBenefit()
        transform_default(src.ExplanationOfBenefit, tgt.ExplanationOfBenefit)
    if src.FamilyMemberHistory:
        tgt.FamilyMemberHistory = malac.models.fhir.r5.FamilyMemberHistory()
        transform_default(src.FamilyMemberHistory, tgt.FamilyMemberHistory)
    if src.Flag:
        tgt.Flag = malac.models.fhir.r5.Flag()
        transform_default(src.Flag, tgt.Flag)
    if src.Goal:
        tgt.Goal = malac.models.fhir.r5.Goal()
        transform_default(src.Goal, tgt.Goal)
    if src.GraphDefinition:
        tgt.GraphDefinition = malac.models.fhir.r5.GraphDefinition()
        transform_default(src.GraphDefinition, tgt.GraphDefinition)
    if src.Group:
        tgt.Group = malac.models.fhir.r5.Group()
        transform_default(src.Group, tgt.Group)
    if src.GuidanceResponse:
        tgt.GuidanceResponse = malac.models.fhir.r5.GuidanceResponse()
        transform_default(src.GuidanceResponse, tgt.GuidanceResponse)
    if src.HealthcareService:
        tgt.HealthcareService = malac.models.fhir.r5.HealthcareService()
        transform_default(src.HealthcareService, tgt.HealthcareService)
    if src.ImagingStudy:
        tgt.ImagingStudy = malac.models.fhir.r5.ImagingStudy()
        transform_default(src.ImagingStudy, tgt.ImagingStudy)
    if src.Immunization:
        tgt.Immunization = malac.models.fhir.r5.Immunization()
        transform_default(src.Immunization, tgt.Immunization)
    if src.ImmunizationEvaluation:
        tgt.ImmunizationEvaluation = malac.models.fhir.r5.ImmunizationEvaluation()
        transform_default(src.ImmunizationEvaluation, tgt.ImmunizationEvaluation)
    if src.ImmunizationRecommendation:
        tgt.ImmunizationRecommendation = malac.models.fhir.r5.ImmunizationRecommendation()
        transform_default(src.ImmunizationRecommendation, tgt.ImmunizationRecommendation)
    if src.ImplementationGuide:
        tgt.ImplementationGuide = malac.models.fhir.r5.ImplementationGuide()
        transform_default(src.ImplementationGuide, tgt.ImplementationGuide)
    if src.Ingredient:
        tgt.Ingredient = malac.models.fhir.r5.Ingredient()
        transform_default(src.Ingredient, tgt.Ingredient)
    if src.InsurancePlan:
        tgt.InsurancePlan = malac.models.fhir.r5.InsurancePlan()
        transform_default(src.InsurancePlan, tgt.InsurancePlan)
    if src.Invoice:
        tgt.Invoice = malac.models.fhir.r5.Invoice()
        transform_default(src.Invoice, tgt.Invoice)
    if src.Library:
        tgt.Library = malac.models.fhir.r5.Library()
        transform_default(src.Library, tgt.Library)
    if src.Linkage:
        tgt.Linkage = malac.models.fhir.r5.Linkage()
        transform_default(src.Linkage, tgt.Linkage)
    if src.List:
        tgt.List = malac.models.fhir.r5.List()
        transform_default(src.List, tgt.List)
    if src.Location:
        tgt.Location = malac.models.fhir.r5.Location()
        transform_default(src.Location, tgt.Location)
    if src.ManufacturedItemDefinition:
        tgt.ManufacturedItemDefinition = malac.models.fhir.r5.ManufacturedItemDefinition()
        transform_default(src.ManufacturedItemDefinition, tgt.ManufacturedItemDefinition)
    if src.Measure:
        tgt.Measure = malac.models.fhir.r5.Measure()
        transform_default(src.Measure, tgt.Measure)
    if src.MeasureReport:
        tgt.MeasureReport = malac.models.fhir.r5.MeasureReport()
        transform_default(src.MeasureReport, tgt.MeasureReport)
    if src.Media:
        transform_default(src.Media, tgt.Media)
    if src.Medication:
        tgt.Medication = malac.models.fhir.r5.Medication()
        transform_default(src.Medication, tgt.Medication)
    if src.MedicationAdministration:
        tgt.MedicationAdministration = malac.models.fhir.r5.MedicationAdministration()
        transform_default(src.MedicationAdministration, tgt.MedicationAdministration)
    if src.MedicationDispense:
        tgt.MedicationDispense = malac.models.fhir.r5.MedicationDispense()
        transform_default(src.MedicationDispense, tgt.MedicationDispense)
    if src.MedicationKnowledge:
        tgt.MedicationKnowledge = malac.models.fhir.r5.MedicationKnowledge()
        transform_default(src.MedicationKnowledge, tgt.MedicationKnowledge)
    if src.MedicationRequest:
        tgt.MedicationRequest = malac.models.fhir.r5.MedicationRequest()
        transform_default(src.MedicationRequest, tgt.MedicationRequest)
    if src.MedicationStatement:
        tgt.MedicationStatement = malac.models.fhir.r5.MedicationStatement()
        transform_default(src.MedicationStatement, tgt.MedicationStatement)
    if src.MedicinalProductDefinition:
        tgt.MedicinalProductDefinition = malac.models.fhir.r5.MedicinalProductDefinition()
        transform_default(src.MedicinalProductDefinition, tgt.MedicinalProductDefinition)
    if src.MessageDefinition:
        tgt.MessageDefinition = malac.models.fhir.r5.MessageDefinition()
        transform_default(src.MessageDefinition, tgt.MessageDefinition)
    if src.MessageHeader:
        tgt.MessageHeader = malac.models.fhir.r5.MessageHeader()
        transform_default(src.MessageHeader, tgt.MessageHeader)
    if src.MolecularSequence:
        tgt.MolecularSequence = malac.models.fhir.r5.MolecularSequence()
        transform_default(src.MolecularSequence, tgt.MolecularSequence)
    if src.NamingSystem:
        tgt.NamingSystem = malac.models.fhir.r5.NamingSystem()
        transform_default(src.NamingSystem, tgt.NamingSystem)
    if src.NutritionOrder:
        tgt.NutritionOrder = malac.models.fhir.r5.NutritionOrder()
        transform_default(src.NutritionOrder, tgt.NutritionOrder)
    if src.NutritionProduct:
        tgt.NutritionProduct = malac.models.fhir.r5.NutritionProduct()
        transform_default(src.NutritionProduct, tgt.NutritionProduct)
    if src.Observation:
        tgt.Observation = malac.models.fhir.r5.Observation()
        transform_default(src.Observation, tgt.Observation)
    if src.ObservationDefinition:
        tgt.ObservationDefinition = malac.models.fhir.r5.ObservationDefinition()
        transform_default(src.ObservationDefinition, tgt.ObservationDefinition)
    if src.OperationDefinition:
        tgt.OperationDefinition = malac.models.fhir.r5.OperationDefinition()
        transform_default(src.OperationDefinition, tgt.OperationDefinition)
    if src.OperationOutcome:
        tgt.OperationOutcome = malac.models.fhir.r5.OperationOutcome()
        transform_default(src.OperationOutcome, tgt.OperationOutcome)
    if src.Organization:
        tgt.Organization = malac.models.fhir.r5.Organization()
        transform_default(src.Organization, tgt.Organization)
    if src.OrganizationAffiliation:
        tgt.OrganizationAffiliation = malac.models.fhir.r5.OrganizationAffiliation()
        transform_default(src.OrganizationAffiliation, tgt.OrganizationAffiliation)
    if src.PackagedProductDefinition:
        tgt.PackagedProductDefinition = malac.models.fhir.r5.PackagedProductDefinition()
        transform_default(src.PackagedProductDefinition, tgt.PackagedProductDefinition)
    if src.Patient:
        tgt.Patient = malac.models.fhir.r5.Patient()
        transform_default(src.Patient, tgt.Patient)
    if src.PaymentNotice:
        tgt.PaymentNotice = malac.models.fhir.r5.PaymentNotice()
        transform_default(src.PaymentNotice, tgt.PaymentNotice)
    if src.PaymentReconciliation:
        tgt.PaymentReconciliation = malac.models.fhir.r5.PaymentReconciliation()
        transform_default(src.PaymentReconciliation, tgt.PaymentReconciliation)
    if src.Person:
        tgt.Person = malac.models.fhir.r5.Person()
        transform_default(src.Person, tgt.Person)
    if src.PlanDefinition:
        tgt.PlanDefinition = malac.models.fhir.r5.PlanDefinition()
        transform_default(src.PlanDefinition, tgt.PlanDefinition)
    if src.Practitioner:
        tgt.Practitioner = malac.models.fhir.r5.Practitioner()
        transform_default(src.Practitioner, tgt.Practitioner)
    if src.PractitionerRole:
        tgt.PractitionerRole = malac.models.fhir.r5.PractitionerRole()
        transform_default(src.PractitionerRole, tgt.PractitionerRole)
    if src.Procedure:
        tgt.Procedure = malac.models.fhir.r5.Procedure()
        transform_default(src.Procedure, tgt.Procedure)
    if src.Provenance:
        tgt.Provenance = malac.models.fhir.r5.Provenance()
        transform_default(src.Provenance, tgt.Provenance)
    if src.Questionnaire:
        tgt.Questionnaire = malac.models.fhir.r5.Questionnaire()
        transform_default(src.Questionnaire, tgt.Questionnaire)
    if src.QuestionnaireResponse:
        tgt.QuestionnaireResponse = malac.models.fhir.r5.QuestionnaireResponse()
        transform_default(src.QuestionnaireResponse, tgt.QuestionnaireResponse)
    if src.RegulatedAuthorization:
        tgt.RegulatedAuthorization = malac.models.fhir.r5.RegulatedAuthorization()
        transform_default(src.RegulatedAuthorization, tgt.RegulatedAuthorization)
    if src.RelatedPerson:
        tgt.RelatedPerson = malac.models.fhir.r5.RelatedPerson()
        transform_default(src.RelatedPerson, tgt.RelatedPerson)
    if src.RequestGroup:
        tgt.RequestOrchestration = malac.models.fhir.r5.RequestOrchestration()
        transform_default(src.RequestGroup, tgt.RequestOrchestration)
    if src.ResearchDefinition:
        transform_default(src.ResearchDefinition, tgt.ResearchDefinition)
    if src.ResearchElementDefinition:
        transform_default(src.ResearchElementDefinition, tgt.ResearchElementDefinition)
    if src.ResearchStudy:
        tgt.ResearchStudy = malac.models.fhir.r5.ResearchStudy()
        transform_default(src.ResearchStudy, tgt.ResearchStudy)
    if src.ResearchSubject:
        tgt.ResearchSubject = malac.models.fhir.r5.ResearchSubject()
        transform_default(src.ResearchSubject, tgt.ResearchSubject)
    if src.RiskAssessment:
        tgt.RiskAssessment = malac.models.fhir.r5.RiskAssessment()
        transform_default(src.RiskAssessment, tgt.RiskAssessment)
    if src.Schedule:
        tgt.Schedule = malac.models.fhir.r5.Schedule()
        transform_default(src.Schedule, tgt.Schedule)
    if src.SearchParameter:
        tgt.SearchParameter = malac.models.fhir.r5.SearchParameter()
        transform_default(src.SearchParameter, tgt.SearchParameter)
    if src.ServiceRequest:
        tgt.ServiceRequest = malac.models.fhir.r5.ServiceRequest()
        transform_default(src.ServiceRequest, tgt.ServiceRequest)
    if src.Slot:
        tgt.Slot = malac.models.fhir.r5.Slot()
        transform_default(src.Slot, tgt.Slot)
    if src.Specimen:
        tgt.Specimen = malac.models.fhir.r5.Specimen()
        transform_default(src.Specimen, tgt.Specimen)
    if src.SpecimenDefinition:
        tgt.SpecimenDefinition = malac.models.fhir.r5.SpecimenDefinition()
        transform_default(src.SpecimenDefinition, tgt.SpecimenDefinition)
    if src.StructureDefinition:
        tgt.StructureDefinition = malac.models.fhir.r5.StructureDefinition()
        transform_default(src.StructureDefinition, tgt.StructureDefinition)
    if src.StructureMap:
        tgt.StructureMap = (malac.models.fhir.r5.StructureMap.subclass or malac.models.fhir.r5.StructureMap)()
        transform_default(src.StructureMap, tgt.StructureMap)
    if src.Subscription:
        tgt.Subscription = malac.models.fhir.r5.Subscription()
        transform_default(src.Subscription, tgt.Subscription)
    if src.SubscriptionStatus:
        tgt.SubscriptionStatus = malac.models.fhir.r5.SubscriptionStatus()
        transform_default(src.SubscriptionStatus, tgt.SubscriptionStatus)
    if src.SubscriptionTopic:
        tgt.SubscriptionTopic = malac.models.fhir.r5.SubscriptionTopic()
        transform_default(src.SubscriptionTopic, tgt.SubscriptionTopic)
    if src.Substance:
        tgt.Substance = malac.models.fhir.r5.Substance()
        transform_default(src.Substance, tgt.Substance)
    if src.SubstanceDefinition:
        tgt.SubstanceDefinition = malac.models.fhir.r5.SubstanceDefinition()
        transform_default(src.SubstanceDefinition, tgt.SubstanceDefinition)
    if src.SupplyDelivery:
        tgt.SupplyDelivery = malac.models.fhir.r5.SupplyDelivery()
        transform_default(src.SupplyDelivery, tgt.SupplyDelivery)
    if src.SupplyRequest:
        tgt.SupplyRequest = malac.models.fhir.r5.SupplyRequest()
        transform_default(src.SupplyRequest, tgt.SupplyRequest)
    if src.Task:
        tgt.Task = malac.models.fhir.r5.Task()
        transform_default(src.Task, tgt.Task)
    if src.TerminologyCapabilities:
        tgt.TerminologyCapabilities = malac.models.fhir.r5.TerminologyCapabilities()
        transform_default(src.TerminologyCapabilities, tgt.TerminologyCapabilities)
    if src.TestReport:
        tgt.TestReport = malac.models.fhir.r5.TestReport()
        transform_default(src.TestReport, tgt.TestReport)
    if src.TestScript:
        tgt.TestScript = malac.models.fhir.r5.TestScript()
        transform_default(src.TestScript, tgt.TestScript)
    if src.ValueSet:
        tgt.ValueSet = malac.models.fhir.r5.ValueSet()
        transform_default(src.ValueSet, tgt.ValueSet)
    if src.VerificationResult:
        tgt.VerificationResult = malac.models.fhir.r5.VerificationResult()
        transform_default(src.VerificationResult, tgt.VerificationResult)
    if src.VisionPrescription:
        tgt.VisionPrescription = malac.models.fhir.r5.VisionPrescription()
        transform_default(src.VisionPrescription, tgt.VisionPrescription)
    if src.Parameters:
        tgt.Parameters = malac.models.fhir.r5.Parameters()
        transform_default(src.Parameters, tgt.Parameters)

def Uri(src, tgt):
    tgt.value = src.value

def String(src, tgt):
    tgt.value = src.value

def Boolean(src, tgt):
    tgt.value = src.value

def DateTime(src, tgt):
    tgt.value = src.value

def Markdown(src, tgt):
    tgt.value = src.value

def Canonical(src, tgt):
    tgt.value = src.value

def Id(src, tgt):
    tgt.value = src.value

def Code(src, tgt):
    tgt.value = src.value

def Instant(src, tgt):
    tgt.value = src.value

def Integer(src, tgt):
    tgt.value = src.value

def StringToId(src, tgt):
    tgt.value = src.value

def Flow(src, tgt):
    pass

def Div(src, tgt):
    tgt = malac.models.fhir.r5.div()
    Flow(src, tgt)

def ContactPointSystemToCode(src, tgt):
    tgt.value = src.value

def Narrative(src, tgt):
    Element(src, tgt)
    v = src.status
    if v:
        match = translate_single('NarrativeStatus', (v if isinstance(v, str) else v.value), 'code')
        tgt.status = string(value=match)
    if src.div:
        tgt.div = malac.models.fhir.r5.div()
        transform_default(src.div, tgt.div)

def unpack_container(resource_container):
    if resource_container.Account is not None:
        return resource_container.Account
    if resource_container.ActivityDefinition is not None:
        return resource_container.ActivityDefinition
    if resource_container.ActorDefinition is not None:
        return resource_container.ActorDefinition
    if resource_container.AdministrableProductDefinition is not None:
        return resource_container.AdministrableProductDefinition
    if resource_container.AdverseEvent is not None:
        return resource_container.AdverseEvent
    if resource_container.AllergyIntolerance is not None:
        return resource_container.AllergyIntolerance
    if resource_container.Appointment is not None:
        return resource_container.Appointment
    if resource_container.AppointmentResponse is not None:
        return resource_container.AppointmentResponse
    if resource_container.ArtifactAssessment is not None:
        return resource_container.ArtifactAssessment
    if resource_container.AuditEvent is not None:
        return resource_container.AuditEvent
    if resource_container.Basic is not None:
        return resource_container.Basic
    if resource_container.Binary is not None:
        return resource_container.Binary
    if resource_container.BiologicallyDerivedProduct is not None:
        return resource_container.BiologicallyDerivedProduct
    if resource_container.BiologicallyDerivedProductDispense is not None:
        return resource_container.BiologicallyDerivedProductDispense
    if resource_container.BodyStructure is not None:
        return resource_container.BodyStructure
    if resource_container.Bundle is not None:
        return resource_container.Bundle
    if resource_container.CapabilityStatement is not None:
        return resource_container.CapabilityStatement
    if resource_container.CarePlan is not None:
        return resource_container.CarePlan
    if resource_container.CareTeam is not None:
        return resource_container.CareTeam
    if resource_container.ChargeItem is not None:
        return resource_container.ChargeItem
    if resource_container.ChargeItemDefinition is not None:
        return resource_container.ChargeItemDefinition
    if resource_container.Citation is not None:
        return resource_container.Citation
    if resource_container.Claim is not None:
        return resource_container.Claim
    if resource_container.ClaimResponse is not None:
        return resource_container.ClaimResponse
    if resource_container.ClinicalImpression is not None:
        return resource_container.ClinicalImpression
    if resource_container.ClinicalUseDefinition is not None:
        return resource_container.ClinicalUseDefinition
    if resource_container.CodeSystem is not None:
        return resource_container.CodeSystem
    if resource_container.Communication is not None:
        return resource_container.Communication
    if resource_container.CommunicationRequest is not None:
        return resource_container.CommunicationRequest
    if resource_container.CompartmentDefinition is not None:
        return resource_container.CompartmentDefinition
    if resource_container.Composition is not None:
        return resource_container.Composition
    if resource_container.ConceptMap is not None:
        return resource_container.ConceptMap
    if resource_container.Condition is not None:
        return resource_container.Condition
    if resource_container.ConditionDefinition is not None:
        return resource_container.ConditionDefinition
    if resource_container.Consent is not None:
        return resource_container.Consent
    if resource_container.Contract is not None:
        return resource_container.Contract
    if resource_container.Coverage is not None:
        return resource_container.Coverage
    if resource_container.CoverageEligibilityRequest is not None:
        return resource_container.CoverageEligibilityRequest
    if resource_container.CoverageEligibilityResponse is not None:
        return resource_container.CoverageEligibilityResponse
    if resource_container.DetectedIssue is not None:
        return resource_container.DetectedIssue
    if resource_container.Device is not None:
        return resource_container.Device
    if resource_container.DeviceAssociation is not None:
        return resource_container.DeviceAssociation
    if resource_container.DeviceDefinition is not None:
        return resource_container.DeviceDefinition
    if resource_container.DeviceDispense is not None:
        return resource_container.DeviceDispense
    if resource_container.DeviceMetric is not None:
        return resource_container.DeviceMetric
    if resource_container.DeviceRequest is not None:
        return resource_container.DeviceRequest
    if resource_container.DeviceUsage is not None:
        return resource_container.DeviceUsage
    if resource_container.DiagnosticReport is not None:
        return resource_container.DiagnosticReport
    if resource_container.DocumentReference is not None:
        return resource_container.DocumentReference
    if resource_container.Encounter is not None:
        return resource_container.Encounter
    if resource_container.EncounterHistory is not None:
        return resource_container.EncounterHistory
    if resource_container.Endpoint is not None:
        return resource_container.Endpoint
    if resource_container.EnrollmentRequest is not None:
        return resource_container.EnrollmentRequest
    if resource_container.EnrollmentResponse is not None:
        return resource_container.EnrollmentResponse
    if resource_container.EpisodeOfCare is not None:
        return resource_container.EpisodeOfCare
    if resource_container.EventDefinition is not None:
        return resource_container.EventDefinition
    if resource_container.Evidence is not None:
        return resource_container.Evidence
    if resource_container.EvidenceReport is not None:
        return resource_container.EvidenceReport
    if resource_container.EvidenceVariable is not None:
        return resource_container.EvidenceVariable
    if resource_container.ExampleScenario is not None:
        return resource_container.ExampleScenario
    if resource_container.ExplanationOfBenefit is not None:
        return resource_container.ExplanationOfBenefit
    if resource_container.FamilyMemberHistory is not None:
        return resource_container.FamilyMemberHistory
    if resource_container.Flag is not None:
        return resource_container.Flag
    if resource_container.FormularyItem is not None:
        return resource_container.FormularyItem
    if resource_container.GenomicStudy is not None:
        return resource_container.GenomicStudy
    if resource_container.Goal is not None:
        return resource_container.Goal
    if resource_container.GraphDefinition is not None:
        return resource_container.GraphDefinition
    if resource_container.Group is not None:
        return resource_container.Group
    if resource_container.GuidanceResponse is not None:
        return resource_container.GuidanceResponse
    if resource_container.HealthcareService is not None:
        return resource_container.HealthcareService
    if resource_container.ImagingSelection is not None:
        return resource_container.ImagingSelection
    if resource_container.ImagingStudy is not None:
        return resource_container.ImagingStudy
    if resource_container.Immunization is not None:
        return resource_container.Immunization
    if resource_container.ImmunizationEvaluation is not None:
        return resource_container.ImmunizationEvaluation
    if resource_container.ImmunizationRecommendation is not None:
        return resource_container.ImmunizationRecommendation
    if resource_container.ImplementationGuide is not None:
        return resource_container.ImplementationGuide
    if resource_container.Ingredient is not None:
        return resource_container.Ingredient
    if resource_container.InsurancePlan is not None:
        return resource_container.InsurancePlan
    if resource_container.InventoryItem is not None:
        return resource_container.InventoryItem
    if resource_container.InventoryReport is not None:
        return resource_container.InventoryReport
    if resource_container.Invoice is not None:
        return resource_container.Invoice
    if resource_container.Library is not None:
        return resource_container.Library
    if resource_container.Linkage is not None:
        return resource_container.Linkage
    if resource_container.List is not None:
        return resource_container.List
    if resource_container.Location is not None:
        return resource_container.Location
    if resource_container.ManufacturedItemDefinition is not None:
        return resource_container.ManufacturedItemDefinition
    if resource_container.Measure is not None:
        return resource_container.Measure
    if resource_container.MeasureReport is not None:
        return resource_container.MeasureReport
    if resource_container.Medication is not None:
        return resource_container.Medication
    if resource_container.MedicationAdministration is not None:
        return resource_container.MedicationAdministration
    if resource_container.MedicationDispense is not None:
        return resource_container.MedicationDispense
    if resource_container.MedicationKnowledge is not None:
        return resource_container.MedicationKnowledge
    if resource_container.MedicationRequest is not None:
        return resource_container.MedicationRequest
    if resource_container.MedicationStatement is not None:
        return resource_container.MedicationStatement
    if resource_container.MedicinalProductDefinition is not None:
        return resource_container.MedicinalProductDefinition
    if resource_container.MessageDefinition is not None:
        return resource_container.MessageDefinition
    if resource_container.MessageHeader is not None:
        return resource_container.MessageHeader
    if resource_container.MolecularSequence is not None:
        return resource_container.MolecularSequence
    if resource_container.NamingSystem is not None:
        return resource_container.NamingSystem
    if resource_container.NutritionIntake is not None:
        return resource_container.NutritionIntake
    if resource_container.NutritionOrder is not None:
        return resource_container.NutritionOrder
    if resource_container.NutritionProduct is not None:
        return resource_container.NutritionProduct
    if resource_container.Observation is not None:
        return resource_container.Observation
    if resource_container.ObservationDefinition is not None:
        return resource_container.ObservationDefinition
    if resource_container.OperationDefinition is not None:
        return resource_container.OperationDefinition
    if resource_container.OperationOutcome is not None:
        return resource_container.OperationOutcome
    if resource_container.Organization is not None:
        return resource_container.Organization
    if resource_container.OrganizationAffiliation is not None:
        return resource_container.OrganizationAffiliation
    if resource_container.PackagedProductDefinition is not None:
        return resource_container.PackagedProductDefinition
    if resource_container.Patient is not None:
        return resource_container.Patient
    if resource_container.PaymentNotice is not None:
        return resource_container.PaymentNotice
    if resource_container.PaymentReconciliation is not None:
        return resource_container.PaymentReconciliation
    if resource_container.Permission is not None:
        return resource_container.Permission
    if resource_container.Person is not None:
        return resource_container.Person
    if resource_container.PlanDefinition is not None:
        return resource_container.PlanDefinition
    if resource_container.Practitioner is not None:
        return resource_container.Practitioner
    if resource_container.PractitionerRole is not None:
        return resource_container.PractitionerRole
    if resource_container.Procedure is not None:
        return resource_container.Procedure
    if resource_container.Provenance is not None:
        return resource_container.Provenance
    if resource_container.Questionnaire is not None:
        return resource_container.Questionnaire
    if resource_container.QuestionnaireResponse is not None:
        return resource_container.QuestionnaireResponse
    if resource_container.RegulatedAuthorization is not None:
        return resource_container.RegulatedAuthorization
    if resource_container.RelatedPerson is not None:
        return resource_container.RelatedPerson
    if resource_container.RequestOrchestration is not None:
        return resource_container.RequestOrchestration
    if resource_container.Requirements is not None:
        return resource_container.Requirements
    if resource_container.ResearchStudy is not None:
        return resource_container.ResearchStudy
    if resource_container.ResearchSubject is not None:
        return resource_container.ResearchSubject
    if resource_container.RiskAssessment is not None:
        return resource_container.RiskAssessment
    if resource_container.Schedule is not None:
        return resource_container.Schedule
    if resource_container.SearchParameter is not None:
        return resource_container.SearchParameter
    if resource_container.ServiceRequest is not None:
        return resource_container.ServiceRequest
    if resource_container.Slot is not None:
        return resource_container.Slot
    if resource_container.Specimen is not None:
        return resource_container.Specimen
    if resource_container.SpecimenDefinition is not None:
        return resource_container.SpecimenDefinition
    if resource_container.StructureDefinition is not None:
        return resource_container.StructureDefinition
    if resource_container.StructureMap is not None:
        return resource_container.StructureMap
    if resource_container.Subscription is not None:
        return resource_container.Subscription
    if resource_container.SubscriptionStatus is not None:
        return resource_container.SubscriptionStatus
    if resource_container.SubscriptionTopic is not None:
        return resource_container.SubscriptionTopic
    if resource_container.Substance is not None:
        return resource_container.Substance
    if resource_container.SubstanceDefinition is not None:
        return resource_container.SubstanceDefinition
    if resource_container.SubstanceNucleicAcid is not None:
        return resource_container.SubstanceNucleicAcid
    if resource_container.SubstancePolymer is not None:
        return resource_container.SubstancePolymer
    if resource_container.SubstanceProtein is not None:
        return resource_container.SubstanceProtein
    if resource_container.SubstanceReferenceInformation is not None:
        return resource_container.SubstanceReferenceInformation
    if resource_container.SubstanceSourceMaterial is not None:
        return resource_container.SubstanceSourceMaterial
    if resource_container.SupplyDelivery is not None:
        return resource_container.SupplyDelivery
    if resource_container.SupplyRequest is not None:
        return resource_container.SupplyRequest
    if resource_container.Task is not None:
        return resource_container.Task
    if resource_container.TerminologyCapabilities is not None:
        return resource_container.TerminologyCapabilities
    if resource_container.TestPlan is not None:
        return resource_container.TestPlan
    if resource_container.TestReport is not None:
        return resource_container.TestReport
    if resource_container.TestScript is not None:
        return resource_container.TestScript
    if resource_container.Transport is not None:
        return resource_container.Transport
    if resource_container.ValueSet is not None:
        return resource_container.ValueSet
    if resource_container.VerificationResult is not None:
        return resource_container.VerificationResult
    if resource_container.VisionPrescription is not None:
        return resource_container.VisionPrescription
    if resource_container.Parameters is not None:
        return resource_container.Parameters
    return None

default_types_maps = {
    (malac.models.fhir.r4.string, malac.models.fhir.r5.id): StringToId,
    (malac.models.fhir.r4.ContactPointSystem, malac.models.fhir.r5.code): ContactPointSystemToCode,
}
default_types_maps_plus = {
    malac.models.fhir.r4.Identifier: Identifier,
    malac.models.fhir.r4.Meta: Meta,
    malac.models.fhir.r4.ContactDetail: ContactDetail,
    malac.models.fhir.r4.ContactPoint: ContactPoint,
    malac.models.fhir.r4.UsageContext: UsageContext,
    malac.models.fhir.r4.Extension: Extension,
    malac.models.fhir.r4.CodeableConcept: CodeableConcept,
    malac.models.fhir.r4.Coding: Coding,
    malac.models.fhir.r4.ResourceContainer: ResourceContainer,
    malac.models.fhir.r4.uri: Uri,
    malac.models.fhir.r4.string: String,
    malac.models.fhir.r4.boolean: Boolean,
    malac.models.fhir.r4.dateTime: DateTime,
    malac.models.fhir.r4.markdown: Markdown,
    malac.models.fhir.r4.canonical: Canonical,
    malac.models.fhir.r4.id: Id,
    malac.models.fhir.r4.code: Code,
    malac.models.fhir.r4.instant: Instant,
    malac.models.fhir.r4.integer: Integer,
    malac.models.fhir.r4.div: Div,
    malac.models.fhir.r4.Narrative: Narrative,
    malac.models.fhir.r4.Resource: Resource,
    malac.models.fhir.r4.DomainResource: DomainResource,
    malac.models.fhir.r4.ConceptMap: ConceptMap,
    malac.models.fhir.r4.StructureMap: StructureMap,
}

def transform_default(source, target, target_type=None):
    target_type = target_type or type(target)
    source_type = type(source)
    while source_type is not None:
        default_map = default_types_maps.get((source_type, target_type))
        if default_map:
            default_map(source, target)
            return
        source_type = source_type.__bases__[0] if source_type.__bases__ else None
    source_type = type(source)
    while source_type is not None:
        default_map_plus = default_types_maps_plus.get(source_type)
        if default_map_plus:
            default_map_plus(source, target)
            return
        source_type = source_type.__bases__[0] if source_type.__bases__ else None
    raise BaseException('No default transform found for %s -> %s' % (type(source), target_type))

def translate_unmapped(url, code):
    if url == 'http://hl7.org/fhir/ConceptMap/special-oid2uri': return [{'uri': 'urn:oid:%s' % code}]
    if url == 'OIDtoURI': return [{'code': 'urn:oid:%s' % code}]
    if url == 'StructureMapGroupTypeMode': return [{'code': 'none'}]
    raise BaseException('Code %s could not be mapped to any code in concept map %s and no exception defined' % (code, url))

def translate_single(url, code, out_type):
    trans_out = translate(url=url, code=code, silent=True)
    matches = [match['concept'] for match in trans_out['match'] if match['equivalence']=='equivalent' or match['equivalence']=='equal']
    # if there are mutliple 'equivalent' or 'equal' matches and CodeableConcept is not the output param, than throw an error
    if len(matches) > 1:
        raise BaseException("There are multiple 'equivalent' or 'equal' matches in the results of the translate and output type is not CodeableConcept!")
    elif len(matches) == 0:
        matches = translate_unmapped(url=url, code=code)
    if out_type == "Coding":
        return malac.models.fhir.r5.Coding(system=malac.models.fhir.r5.uri(value=matches[0]['system']), version=malac.models.fhir.r5.string(value=matches[0]['version']), code=malac.models.fhir.r5.string(value=matches[0]['code']), display=malac.models.fhir.r5.string(value=matches[0]['display']), userSelected=malac.models.fhir.r5.string(value=matches[0]['userSelected']))
    else:
        return matches[0][out_type]

if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    transform(args.source, args.target)
