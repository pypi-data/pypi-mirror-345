/*********************************************************************
 * Copyright
 *
 * IBM Confidential
 * (C) COPYRIGHT IBM CORP. 2023
 * IBM Zurich Research Laboratory - Cloud Storage & Analytics Group
 * All rights reserved.
 *
 * This software contains the valuable trade secrets of IBM or its
 * licensors.  The software is protected under international copyright
 * laws and treaties.  This software may only be used in accordance with
 * the terms of its accompanying license agreement.
 *
 * Authors      :
 *
 * End Copyright
 ********************************************************************/

#include <vector>
#include <map>
#include <set>
#include <string>
#include <functional>
#include <cmath>
#include <iostream>

#include <rapidjson/document.h>
#include <rapidjson/filereadstream.h>

#include "DenseDataset.hpp"
#include "DataSchema.hpp"
#include "AnyDataset.hpp"
#include "Transformer.hpp"
#include "FunctionTransformer.hpp"
#include "Normalizer.hpp"
#include "KBinsDiscretizer.hpp"
#include "OneHotEncoder.hpp"
#include "OrdinalEncoder.hpp"
#include "TargetEncoder.hpp"
#include "Constants.hpp"

#include "Pipeline.hpp"

namespace snapml {

Pipeline::Pipeline() { }

Pipeline::~Pipeline()

{
    for (snapml::Transformer* t : preprocessing_steps)
        delete t;
}

void Pipeline::get_data_schema(rapidjson::Document& doc)

{
    data_schema.num_features = 0;
    if (doc.HasMember("data_schema") && doc["data_schema"].IsObject()) {
        if (doc["data_schema"].HasMember("num_indices") && doc["data_schema"]["num_indices"].IsArray()) {
            for (rapidjson::SizeType i = 0; i < doc["data_schema"]["num_indices"].Size(); i++) {
                if (doc["data_schema"]["num_indices"][i].IsInt()) {
                    data_schema.indices_num_features.push_back(doc["data_schema"]["num_indices"][i].GetInt());
                    data_schema.num_features++;
                }
            }
        }
        if (doc["data_schema"].HasMember("cat_indices") && doc["data_schema"]["cat_indices"].IsArray()) {
            for (rapidjson::SizeType i = 0; i < doc["data_schema"]["cat_indices"].Size(); i++) {
                if (doc["data_schema"]["cat_indices"][i].IsInt()) {
                    data_schema.indices_cat_features.push_back(doc["data_schema"]["cat_indices"][i].GetInt());
                    data_schema.num_features++;
                }
            }
        }
    } else {
        throw std::runtime_error("Could not parse data_schema in Json file");
    }
}

void Pipeline::get_normalizer(rapidjson::SizeType i, const rapidjson::Value& value, std::set<uint32_t>& index_list)

{
    Normalizer::Params params;
    if (value[i].HasMember("params") && value[i]["params"].HasMember("norm")) {
        std::string norm_str = value[i]["params"]["norm"].GetString();
        if (norm_str == "l2")
            params.norm = Normalizer::Params::Norm::l2;
        else if (norm_str == "l1")
            params.norm = Normalizer::Params::Norm::l1;
        else if (norm_str == "max")
            params.norm = Normalizer::Params::Norm::max;
        else
            throw std::runtime_error("Unknown norm provided for Normalizer");
    }
    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new Normalizer(params)));
}

void Pipeline::get_function_transformer(rapidjson::SizeType i, const rapidjson::Value& value,
                                        std::set<uint32_t>& index_list)

{
    FunctionTransformer::Params params;
    if (value[i].HasMember("params") && value[i]["params"].HasMember("func")) {
        std::string func_str = value[i]["params"]["func"].GetString();
        if (func_str == "log1p")
            params.func = [](float x) { return std::log(x + 1); };
        else if (func_str == "log10")
            params.func = [](float x) { return std::log10(x); };
        else if (func_str == "log2")
            params.func = [](float x) { return std::log2(x); };
        else if (func_str == "log")
            params.func = [](float x) { return std::log(x); };
        else
            throw std::runtime_error("Function provided for FunctionTransformer " + func_str + " not supported.");
    }
    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new FunctionTransformer(params)));
}

void Pipeline::get_k_bins_discretizer(rapidjson::SizeType i, const rapidjson::Value& value,
                                      std::set<uint32_t>& index_list)

{
    KBinsDiscretizer::Params params;

    if (value[i].HasMember("params")) {
        if (value[i]["params"].HasMember("n_bins")) {
            params.n_bins = value[i]["params"]["n_bins"].GetInt();
        }
        if (value[i]["params"].HasMember("encode")) {
            std::string encode_str = value[i]["params"]["encode"].GetString();
            if (encode_str == "onehot")
                params.encode = KBinsDiscretizer::Params::Encode::onehot;
            else if (encode_str == "onehot-dense")
                params.encode = KBinsDiscretizer::Params::Encode::onehot_dense;
            else if (encode_str == "ordinal")
                params.encode = KBinsDiscretizer::Params::Encode::ordinal;
            else
                throw std::runtime_error("Could not parse params in KBinsDiscretizer");
        }
    } else {
        throw std::runtime_error("Could not parse params in KBinsDiscretizer");
    }
    if (params.encode == KBinsDiscretizer::Params::Encode::onehot
        || params.encode == KBinsDiscretizer::Params::Encode::onehot_dense)
        throw std::runtime_error("onehot and onehot-dense encoding is not suppored for KBinsDiscretizer");
    if (value[i].HasMember("data") && value[i]["data"].HasMember("bin_edges")
        && value[i]["data"]["bin_edges"].IsArray()) {
        for (rapidjson::SizeType j = 0; j < value[i]["data"]["bin_edges"].Size(); j++) {
            if (value[i]["data"]["bin_edges"][j].IsArray()) {
                std::vector<float> bin_edge_vec;
                for (rapidjson::SizeType j_in = 0; j_in < value[i]["data"]["bin_edges"][j].Size(); j_in++) {
                    bin_edge_vec.push_back(value[i]["data"]["bin_edges"][j][j_in].GetFloat());
                }
                params.bin_edges.push_back(bin_edge_vec);
            }
        }
    } else {
        throw std::runtime_error("Could not parse bin_edges in KBinsDiscretizer");
    }
    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new KBinsDiscretizer(params)));
}

void Pipeline::get_one_hot_encoder(rapidjson::SizeType i, const rapidjson::Value& value, std::set<uint32_t>& index_list)

{
    OneHotEncoder::Params params;

    if (value[i].HasMember("params")) {
        if (value[i]["params"].HasMember("handle_unknown")) {
            std::string handle_unknown_str = value[i]["params"]["handle_unknown"].GetString();
            if (handle_unknown_str == "error") {
                params.handle_unkown = OneHotEncoder::Params::HandleUnknown::error;
            } else if (handle_unknown_str == "ignore") {
                params.handle_unkown = OneHotEncoder::Params::HandleUnknown::ignore;
            } else if (handle_unknown_str == "infrequent_if_exist") {
                params.handle_unkown = OneHotEncoder::Params::HandleUnknown::infrequent_if_exist;
            } else {
                throw std::runtime_error("Could not parse params in OneHotEncoder");
            }
        }
        if (value[i]["params"].HasMember("sparse_output")) {
            params.sparse_output = value[i]["params"]["sparse_output"].GetBool();
        }
    } else {
        throw std::runtime_error("Could not parse params in OneHotEncoder");
    }
    if (params.handle_unkown != OneHotEncoder::Params::HandleUnknown::ignore)
        throw std::runtime_error(
            "Only 'ignore' is supported as value of the 'handle_unknown' parameter for OneHotEncoder");
    if (params.sparse_output == true)
        throw std::runtime_error(
            "Only 'false' is supported as value of the 'sparse_output' parameter for OneHotEncoder");

    bool is_string;
    if (value[i].HasMember("data") && value[i]["data"].HasMember("categories")
        && value[i]["data"]["categories"].IsArray()) {
        for (rapidjson::SizeType j = 0; j < value[i]["data"]["categories"].Size(); j++) {
            if (value[i]["data"]["categories"][j].IsArray()) {
                if (value[i]["data"]["categories"][j][0].IsString())
                    is_string = true;
                else
                    is_string = false;
                for (rapidjson::SizeType j_in = 0; j_in < value[i]["data"]["categories"][j].Size(); j_in++) {
                    if (j_in == 0) {
                        if (is_string)
                            params.categories.push_back({ { value[i]["data"]["categories"][j][j_in].GetString(), 0 } });
                        else
                            params.categories.push_back(
                                { { std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat()), 0 } });
                    } else {
                        if (is_string)
                            params.categories[j][value[i]["data"]["categories"][j][j_in].GetString()] = j_in;
                        else
                            params.categories[j][std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat())]
                                = j_in;
                    }
                }
            }
        }
    } else {
        throw std::runtime_error("Could not parse categories in OneHotEncoder");
    }
    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new OneHotEncoder(params)));
}

void Pipeline::get_ordinal_encoder(rapidjson::SizeType i, const rapidjson::Value& value, std::set<uint32_t>& index_list)

{
    OrdinalEncoder::Params params;

    if (value[i].HasMember("params")) {
        if (value[i]["params"].HasMember("handle_unknown")) {
            std::string handle_unknown_str = value[i]["params"]["handle_unknown"].GetString();
            if (handle_unknown_str == "error") {
                params.handle_unkown = OrdinalEncoder::Params::HandleUnknown::error;
            } else if (handle_unknown_str == "use_encoded_value") {
                params.handle_unkown = OrdinalEncoder::Params::HandleUnknown::use_encoded_value;
            } else {
                throw std::runtime_error("Could not parse params in OrdinalEncoder");
            }
        }
        if (value[i]["params"].HasMember("unknown_value")) {
            params.unknown_value = value[i]["params"]["unknown_value"].GetInt();
        }
    } else {
        throw std::runtime_error("Could not parse params in OrdinalEncoder");
    }
    if (params.handle_unkown != OrdinalEncoder::Params::HandleUnknown::use_encoded_value)
        throw std::runtime_error(
            "Only 'use_encoded_value' is supported as value of the 'handle_unknown' parameter for OrdinalEncoder");

    bool is_string;
    if (value[i].HasMember("data") && value[i]["data"].HasMember("categories")
        && value[i]["data"]["categories"].IsArray()) {
        for (rapidjson::SizeType j = 0; j < value[i]["data"]["categories"].Size(); j++) {
            if (value[i]["data"]["categories"][j].IsArray()) {
                if (value[i]["data"]["categories"][j][0].IsString())
                    is_string = true;
                else
                    is_string = false;
                for (rapidjson::SizeType j_in = 0; j_in < value[i]["data"]["categories"][j].Size(); j_in++) {
                    if (j_in == 0) {
                        if (is_string)
                            params.categories.push_back({ { value[i]["data"]["categories"][j][j_in].GetString(), 0 } });
                        else
                            params.categories.push_back(
                                { { std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat()), 0 } });
                    } else {
                        if (is_string)
                            params.categories[j][value[i]["data"]["categories"][j][j_in].GetString()] = j_in;
                        else
                            params.categories[j][std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat())]
                                = j_in;
                    }
                }
            }
        }
    } else {
        throw std::runtime_error("Could not parse categories in OrdinalEncoder");
    }
    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new OrdinalEncoder(params)));
}

void Pipeline::get_target_encoder(rapidjson::SizeType i, const rapidjson::Value& value, std::set<uint32_t>& index_list)

{
    TargetEncoder::Params params;

    bool is_string;

    if (!value[i].HasMember("data") || !value[i]["data"].HasMember("categories")
        || !value[i]["data"]["categories"].IsArray()) {
        throw std::runtime_error("Could not parse categories in TargetEncoder");
    }

    if (!value[i]["data"].HasMember("encodings") || !value[i]["data"]["encodings"].IsArray()) {
        throw std::runtime_error("Could not parse encodings in TargetEncoder");
    }

    for (rapidjson::SizeType j = 0; j < value[i]["data"]["categories"].Size(); j++) {
        if (value[i]["data"]["categories"][j].IsArray() && value[i]["data"]["encodings"][j].IsArray()) {
            if (value[i]["data"]["categories"][j][0].IsString())
                is_string = true;
            else
                is_string = false;
            for (rapidjson::SizeType j_in = 0; j_in < value[i]["data"]["categories"][j].Size(); j_in++) {
                if (j_in == 0) {
                    if (is_string)
                        params.categories.push_back({ { value[i]["data"]["categories"][j][j_in].GetString(),
                                                        value[i]["data"]["encodings"][j][j_in].GetFloat() } });
                    else
                        params.categories.push_back(
                            { { std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat()),
                                value[i]["data"]["encodings"][j][j_in].GetFloat() } });
                } else {
                    if (is_string)
                        params.categories[j][value[i]["data"]["categories"][j][j_in].GetString()]
                            = value[i]["data"]["encodings"][j][j_in].GetFloat();
                    else
                        params.categories[j][std::to_string(value[i]["data"]["categories"][j][j_in].GetFloat())]
                            = value[i]["data"]["encodings"][j][j_in].GetFloat();
                }
            }
        }
    }

    if (value[i]["data"].HasMember("target_mean"))
        params.target_mean = value[i]["data"]["target_mean"].GetFloat();

    params.index_list = index_list;
    preprocessing_steps.push_back(reinterpret_cast<Transformer*>(new TargetEncoder(params)));
}

void Pipeline::import(std::string json_filename)
{
    char                readBuffer[65536];
    rapidjson::Document doc {};

    if (json_filename.compare(0, 49, snapml::JSON_STRING) == 0) {
        doc.Parse(json_filename.substr(49, -1).c_str());
    } else {
        // Open the file
        FILE* fp = fopen(json_filename.c_str(), "rb");
        if (fp == 0)
            throw std::runtime_error("could not open file " + json_filename);

        try {

            // Read the file into a buffer
            rapidjson::FileReadStream is(fp, readBuffer, sizeof(readBuffer));

            // Parse the JSON document
            doc.ParseStream(is);

        } catch (const std::exception& e) {
            fclose(fp);
            throw std::runtime_error(std::string("Reading and parsing the JSON doc stream failed, error: ") + e.what());
        }

        // Close the file
        fclose(fp);
    }

    DataSchema data_schema;

    // Extract values from the JSON
    if (!doc.IsObject())
        throw std::runtime_error("Could not parse a pipeline in Json file");

    get_data_schema(doc);
    if (doc.HasMember("transformers") && doc["transformers"].IsObject()) {
        for (rapidjson::Value::ConstMemberIterator it = doc["transformers"].MemberBegin();
             it != doc["transformers"].MemberEnd(); it++) {
            // const char* name = it->name.GetString();
            // std::cout << "NAME: " << it->name.GetString() << std::endl;
            const rapidjson::Value& value = it->value;

            if (!value.IsArray())
                throw std::runtime_error("Incorrect transformer format in Json file");

            for (rapidjson::SizeType i = 0; i < value.Size(); i++) {
                if (!value[i].IsObject())
                    throw std::runtime_error("Incorrect transformer format in Json file");

                std::set<uint32_t> index_list;
                if (value[i].HasMember("columns") && value[i]["columns"].IsArray()) {
                    for (rapidjson::SizeType k = 0; k < value[i]["columns"].Size(); k++) {
                        if (value[i]["columns"][k].IsInt()) {
                            index_list.insert(value[i]["columns"][k].GetInt());
                        }
                    }
                } else {
                    throw std::runtime_error("Could not parse index list in transformer " + std::to_string(i));
                }
                if (value[i].HasMember("type")) {
                    if (strcmp(value[i]["type"].GetString(), "Normalizer") == 0) {
                        get_normalizer(i, value, index_list);
                    } else if (strcmp(value[i]["type"].GetString(), "FunctionTransformer") == 0) {
                        get_function_transformer(i, value, index_list);
                    } else if (strcmp(value[i]["type"].GetString(), "KBinsDiscretizer") == 0) {
                        get_k_bins_discretizer(i, value, index_list);
                    } else if (strcmp(value[i]["type"].GetString(), "OneHotEncoder") == 0) {
                        get_one_hot_encoder(i, value, index_list);
                    } else if (strcmp(value[i]["type"].GetString(), "OrdinalEncoder") == 0) {
                        get_ordinal_encoder(i, value, index_list);
                    } else if (strcmp(value[i]["type"].GetString(), "TargetEncoder") == 0) {
                        get_target_encoder(i, value, index_list);
                    }
                } else {
                    throw std::runtime_error("Could not parse type in transformer " + std::to_string(i));
                }
            }
        }
    } else {
        throw std::runtime_error("Could not parse transformers in Json file");
    }
}

snapml::DenseDataset Pipeline::transform(snapml::AnyDataset& dataset)
{
    for (snapml::Transformer* t : preprocessing_steps)
        t->transform(dataset);

    return dataset.convertToDenseDataset();
}

snapml::DataSchema Pipeline::get_schema() { return data_schema; }

}
