//==============================================================================
// Copyright 2025 Vajra Team; Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//==============================================================================
#include "native/utils/ProtoUtils.h"

#include "commons/Logging.h"
//==============================================================================
namespace vajra {
//==============================================================================
vajra_proto::StepMicrobatchOutputs ProtoUtils::StepMicrobatchOutputsToProto(
    const vajra::StepMicrobatchOutputs& obj) {
  vajra_proto::StepMicrobatchOutputs proto;
  proto.set_schedule_id(obj.schedule_id);
  return proto;
}
//==============================================================================
vajra::StepMicrobatchOutputs ProtoUtils::StepMicrobatchOutputsFromProto(
    const vajra_proto::StepMicrobatchOutputs& proto) {
  return vajra::StepMicrobatchOutputs(proto.schedule_id());
}
//==============================================================================
vajra_proto::StepOutputs ProtoUtils::StepOutputsToProto(
    const vajra::StepOutputs& obj) {
  vajra_proto::StepOutputs proto;
  proto.set_schedule_id(obj.schedule_id);
  proto.mutable_sampler_outputs()->Reserve(obj.sampler_outputs.size());
  for (const auto& sampler_output_opt : obj.sampler_outputs) {
    if (sampler_output_opt.has_value()) {
      proto.add_sampler_outputs()->CopyFrom(
          ProtoUtils::SamplerOutputToProto(sampler_output_opt.value()));
    } else {
      proto.add_sampler_outputs();  // Placeholder for nullopt
    }
  }
  return proto;
}
//==============================================================================
vajra::StepOutputs ProtoUtils::StepOutputsFromProto(
    const vajra_proto::StepOutputs& proto) {
  const auto& sampler_outputs_proto = proto.sampler_outputs();
  SamplerOutputs optional_sampler_outputs;
  optional_sampler_outputs.reserve(sampler_outputs_proto.size());
  for (const auto& sampler_output_proto : sampler_outputs_proto) {
    if (sampler_output_proto.ByteSizeLong() > 0) {  // Check for placeholder
      optional_sampler_outputs.push_back(std::make_optional(
          ProtoUtils::SamplerOutputFromProto(sampler_output_proto)));
    } else {
      optional_sampler_outputs.push_back(std::nullopt);
    }
  }
  return vajra::StepOutputs(proto.schedule_id(),
                            std::move(optional_sampler_outputs));
}
//==============================================================================
vajra_proto::StepInputs ProtoUtils::StepInputsToProto(
    const vajra::StepInputs& obj) {
  vajra_proto::StepInputs proto;
  if (obj.scheduler_output) {
    proto.mutable_scheduler_output()->CopyFrom(
        ProtoUtils::SchedulerOutputToProto(obj.scheduler_output));
  }
  proto.mutable_new_seq_params()->Reserve(obj.new_seq_params.size());
  for (const auto& sequence_params : obj.new_seq_params) {
    proto.add_new_seq_params()->CopyFrom(
        ProtoUtils::SequenceParamsToProto(sequence_params));
  }
  proto.mutable_pending_step_outputs()->Reserve(
      obj.pending_step_outputs.size());
  for (const auto& pending_step_output : obj.pending_step_outputs) {
    proto.add_pending_step_outputs()->CopyFrom(
        ProtoUtils::PendingStepOutputToProto(pending_step_output));
  }
  return proto;
}
//==============================================================================
vajra::StepInputs ProtoUtils::StepInputsFromProto(
    const vajra_proto::StepInputs& proto) {
  SchedulerOutputPtr scheduler_output_ptr = nullptr;
  if (proto.has_scheduler_output()) {
    scheduler_output_ptr = std::make_shared<SchedulerOutput>(
        ProtoUtils::SchedulerOutputFromProto(proto.scheduler_output()));
  }
  std::vector<vajra::SequenceParams> new_seq_params;
  new_seq_params.reserve(proto.new_seq_params_size());
  for (const auto& new_seq_param_proto : proto.new_seq_params()) {
    new_seq_params.push_back(
        ProtoUtils::SequenceParamsFromProto(new_seq_param_proto));
  }
  std::vector<vajra::PendingStepOutput> pending_step_outputs;
  pending_step_outputs.reserve(proto.pending_step_outputs_size());
  for (const auto& pending_step_output_proto : proto.pending_step_outputs()) {
    pending_step_outputs.push_back(
        ProtoUtils::PendingStepOutputFromProto(pending_step_output_proto));
  }
  return vajra::StepInputs(std::move(scheduler_output_ptr),
                           std::move(new_seq_params),
                           std::move(pending_step_outputs));
}
//==============================================================================
vajra_proto::SamplerOutput ProtoUtils::SamplerOutputToProto(
    const vajra::SamplerOutputPtr& obj) {  // Added const&
  vajra_proto::SamplerOutput proto;
  if (!obj) return proto;
  proto.set_schedule_id(obj->GetScheduleId());
  proto.set_seq_id(obj->GetSeqId());
  const auto& tokens = obj->GetOutputTokens();
  proto.mutable_output_tokens()->Assign(tokens.begin(), tokens.end());
  return proto;
}
//==============================================================================
vajra::SamplerOutputPtr ProtoUtils::SamplerOutputFromProto(
    const vajra_proto::SamplerOutput& proto) {
  std::vector<TokenId> output_tokens = ExtractRepeatedField<TokenId>(
      proto.output_tokens());  // Use helper from header
  return std::make_shared<vajra::SamplerOutput>(
      proto.schedule_id(), proto.seq_id(), std::move(output_tokens));
}
//==============================================================================
vajra_proto::SchedulerOutput ProtoUtils::SchedulerOutputToProto(
    const vajra::SchedulerOutputPtr& obj) {  // Added const&
  vajra_proto::SchedulerOutput proto;
  if (!obj) return proto;
  proto.set_schedule_id(obj->id);
  const auto& ignored_ids = obj->ignored_seq_ids;
  proto.mutable_ignored_seq_ids()->Assign(ignored_ids.begin(),
                                          ignored_ids.end());
  const auto& preempted_ids = obj->preempted_seq_ids;
  proto.mutable_preempted_seq_ids()->Assign(preempted_ids.begin(),
                                            preempted_ids.end());
  proto.mutable_seq_schedule_metadata_list()->Reserve(
      obj->seq_schedule_metadata_list.size());
  for (const auto& seq_schedule_metadata_ptr :
       obj->seq_schedule_metadata_list) {
    proto.add_seq_schedule_metadata_list()->CopyFrom(
        SequenceScheduleMetadataToProto(seq_schedule_metadata_ptr));
  }
  return proto;
}
//==============================================================================
vajra::SchedulerOutput ProtoUtils::SchedulerOutputFromProto(
    const vajra_proto::SchedulerOutput& proto) {
  std::vector<std::string> ignored_seq_ids = ExtractRepeatedField<std::string>(
      proto.ignored_seq_ids());  // Use helper from header
  std::vector<std::string> preempted_seq_ids =
      ExtractRepeatedField<std::string>(
          proto.preempted_seq_ids());  // Use helper from header
  SequenceScheduleMetadataPtrList seq_schedule_metadata_list;
  seq_schedule_metadata_list.reserve(proto.seq_schedule_metadata_list_size());
  for (const auto& meta_proto : proto.seq_schedule_metadata_list()) {
    seq_schedule_metadata_list.push_back(
        SequenceScheduleMetadataFromProto(meta_proto));
  }
  return vajra::SchedulerOutput(proto.schedule_id(), std::move(ignored_seq_ids),
                                std::move(preempted_seq_ids),
                                std::move(seq_schedule_metadata_list));
}
//==============================================================================
vajra_proto::SequenceParams ProtoUtils::SequenceParamsToProto(
    const vajra::SequenceParams& obj) {
  vajra_proto::SequenceParams proto;
  proto.set_seq_id(obj.seq_id);
  proto.set_prompt(obj.prompt);
  if (obj.prompt_token_ids) {
    const auto& token_ids = *obj.prompt_token_ids;
    proto.mutable_prompt_token_ids()->Assign(token_ids.begin(),
                                             token_ids.end());
  }
  proto.set_block_size(obj.block_size);
  proto.set_eos_token_id(obj.eos_token_id);
  proto.set_arrival_time(obj.arrival_time);
  proto.mutable_sampling_params()->CopyFrom(
      SamplingParamsToProto(obj.sampling_params));
  return proto;
}

vajra::SequenceParams ProtoUtils::SequenceParamsFromProto(
    const vajra_proto::SequenceParams& proto) {
  auto prompt_token_ids_vec = ExtractRepeatedField<TokenId>(
      proto.prompt_token_ids());  // Use helper from header
  auto prompt_token_ids_ptr =
      std::make_shared<std::vector<TokenId>>(std::move(prompt_token_ids_vec));
  return vajra::SequenceParams(
      proto.seq_id(), proto.prompt(), std::move(prompt_token_ids_ptr),
      proto.block_size(), proto.eos_token_id(), proto.arrival_time(),
      SamplingParamsFromProto(proto.sampling_params()));
}
//==============================================================================
vajra_proto::PendingStepOutput ProtoUtils::PendingStepOutputToProto(
    const vajra::PendingStepOutput& obj) {
  vajra_proto::PendingStepOutput proto;
  if (obj.scheduler_output) {
    proto.mutable_scheduler_output()->CopyFrom(
        SchedulerOutputToProto(obj.scheduler_output));
  }
  proto.mutable_sampler_outputs()->Reserve(obj.sampler_outputs.size());
  for (const auto& sampler_output_opt : obj.sampler_outputs) {
    proto.add_sampler_outputs()->CopyFrom(
        SamplerOutputToProto(sampler_output_opt));
  }
  return proto;
}
//==============================================================================
vajra::PendingStepOutput ProtoUtils::PendingStepOutputFromProto(
    const vajra_proto::PendingStepOutput& proto) {
  SchedulerOutputPtr scheduler_output_ptr = nullptr;
  if (proto.has_scheduler_output()) {
    scheduler_output_ptr = std::make_shared<SchedulerOutput>(
        SchedulerOutputFromProto(proto.scheduler_output()));
  }
  ValidSamplerOutputs sampler_outputs;
  sampler_outputs.reserve(proto.sampler_outputs_size());
  for (const auto& sampler_output_proto : proto.sampler_outputs()) {
    sampler_outputs.push_back(SamplerOutputFromProto(sampler_output_proto));
  }
  return vajra::PendingStepOutput(std::move(scheduler_output_ptr),
                                  std::move(sampler_outputs));
}
//==============================================================================
vajra_proto::SequenceScheduleMetadata
ProtoUtils::SequenceScheduleMetadataToProto(
    const vajra::SequenceScheduleMetadataPtr& obj) {  // Added const&
  vajra_proto::SequenceScheduleMetadata proto;
  if (!obj) return proto;
  proto.set_schedule_id(obj->schedule_id);
  proto.set_seq_id(obj->seq_id);
  proto.set_num_q_tokens(static_cast<std::size_t>(obj->num_q_tokens));
  proto.set_is_kvp_request(obj->is_kvp_request);
  google::protobuf::Map<std::size_t, std::size_t>* proto_map =
      proto.mutable_kvp_group_block_counter();
  proto_map->clear();
  for (const auto& pair : obj->kvp_group_block_counter) {
    (*proto_map)[static_cast<std::size_t>(pair.first)] =
        static_cast<std::size_t>(pair.second);
  }
  const auto& group_ids = obj->kvp_group_ids;
  proto.mutable_kvp_group_ids()->Reserve(group_ids.size());
  for (const auto& id : group_ids) {
    proto.add_kvp_group_ids(static_cast<std::size_t>(id));
  }
  return proto;
}
//==============================================================================
vajra::SequenceScheduleMetadataPtr
ProtoUtils::SequenceScheduleMetadataFromProto(
    const vajra_proto::SequenceScheduleMetadata& proto) {
  std::unordered_map<std::size_t, std::size_t> kvp_group_block_counter;
  for (const auto& pair : proto.kvp_group_block_counter()) {
    kvp_group_block_counter[static_cast<std::size_t>(pair.first)] =
        static_cast<std::size_t>(pair.second);
  }
  std::vector<std::size_t> kvp_group_ids =
      ExtractRepeatedField<std::size_t>(proto.kvp_group_ids());
  return std::make_shared<vajra::SequenceScheduleMetadata>(
      proto.schedule_id(), proto.seq_id(),
      static_cast<std::size_t>(proto.num_q_tokens()),
      std::move(kvp_group_block_counter), std::move(kvp_group_ids));
}
//==============================================================================
vajra_proto::SamplingParams ProtoUtils::SamplingParamsToProto(
    const vajra::SamplingParams& obj) {
  vajra_proto::SamplingParams proto;
  proto.set_temperature(obj.temperature);
  proto.set_top_p(obj.top_p);
  proto.set_top_k(obj.top_k);
  proto.set_ignore_eos(obj.ignore_eos);
  proto.set_max_tokens(obj.max_tokens);
  return proto;
}
//==============================================================================
vajra::SamplingParams ProtoUtils::SamplingParamsFromProto(
    const vajra_proto::SamplingParams& proto) {
  return vajra::SamplingParams(proto.temperature(), proto.top_p(),
                               proto.top_k(), proto.ignore_eos(),
                               proto.max_tokens());
}
//==============================================================================
vajra_proto::ModelConfig ProtoUtils::ModelConfigToProto(
    const vajra::ModelConfig& obj) {
  vajra_proto::ModelConfig proto;
  proto.set_model(obj.model);
  proto.set_trust_remote_code(obj.trust_remote_code);
  if (obj.download_dir.has_value()) {
    proto.set_download_dir(obj.download_dir.value());
  }
  proto.set_load_format(obj.load_format);
  proto.set_dtype(obj.dtype);
  proto.set_seed(obj.seed);
  if (obj.revision.has_value()) {
    proto.set_revision(obj.revision.value());
  }
  proto.set_max_model_len(obj.max_model_len);
  proto.set_total_num_layers(obj.total_num_layers);
  proto.set_total_num_q_heads(obj.total_num_q_heads);
  proto.set_total_num_kv_heads(obj.total_num_kv_heads);
  proto.set_hidden_size(obj.hidden_size);
  return proto;
}
//==============================================================================
vajra::ModelConfig ProtoUtils::ModelConfigFromProto(
    const vajra_proto::ModelConfig& proto) {
  std::optional<std::string> download_dir =
      proto.has_download_dir() ? std::make_optional(proto.download_dir())
                               : std::nullopt;
  std::optional<std::string> revision =
      proto.has_revision() ? std::make_optional(proto.revision())
                           : std::nullopt;
  return vajra::ModelConfig(proto.model(), proto.trust_remote_code(),
                            std::move(download_dir), proto.load_format(),
                            proto.dtype(), proto.seed(), std::move(revision),
                            proto.max_model_len(), proto.total_num_layers(),
                            proto.total_num_q_heads(),
                            proto.total_num_kv_heads(), proto.hidden_size());
}
//==============================================================================
// RemoteInferenceRequest conversion functions
//==============================================================================
vajra_proto::ProcessRequest ProtoUtils::ProcessRequestToProto(
    const vajra::ProcessRequest& obj) {
  vajra_proto::ProcessRequest proto;
  proto.set_request_id(obj.request_id);
  proto.set_prompt(obj.prompt);
  proto.mutable_sampling_params()->CopyFrom(
      SamplingParamsToProto(obj.sampling_params));
  return proto;
}

vajra::ProcessRequest ProtoUtils::ProcessRequestFromProto(
    const vajra_proto::ProcessRequest& proto) {
  return vajra::ProcessRequest(
      proto.request_id(), proto.prompt(),
      SamplingParamsFromProto(proto.sampling_params()));
}

vajra_proto::AbortRequest ProtoUtils::AbortRequestToProto(
    const vajra::AbortRequest& obj) {
  vajra_proto::AbortRequest proto;
  proto.set_request_id(obj.request_id);
  return proto;
}

vajra::AbortRequest ProtoUtils::AbortRequestFromProto(
    const vajra_proto::AbortRequest& proto) {
  return vajra::AbortRequest(proto.request_id());
}

vajra_proto::StartupRequest ProtoUtils::StartupRequestToProto(
    const vajra::StartupRequest& obj) {
  vajra_proto::StartupRequest proto;
  proto.set_client_ready(obj.client_ready);
  return proto;
}

vajra::StartupRequest ProtoUtils::StartupRequestFromProto(
    const vajra_proto::StartupRequest& proto) {
  return vajra::StartupRequest(proto.client_ready());
}

vajra_proto::ConfigRequest ProtoUtils::ConfigRequestToProto(
    const vajra::ConfigRequest& obj) {
  vajra_proto::ConfigRequest proto;
  proto.set_request_id(obj.request_id);
  return proto;
}

vajra::ConfigRequest ProtoUtils::ConfigRequestFromProto(
    const vajra_proto::ConfigRequest& proto) {
  return vajra::ConfigRequest(proto.request_id());
}

vajra_proto::RemoteInferenceRequest ProtoUtils::RemoteInferenceRequestToProto(
    const vajra::RemoteInferenceRequest& obj) {
  vajra_proto::RemoteInferenceRequest proto;
  switch (obj.type) {
    case vajra::RemoteInferenceRequest::Type::PROCESS:
      ASSERT_VALID_RUNTIME(obj.process_request.has_value(),
                           "Invalid value for process_request");
      proto.mutable_process_request()->CopyFrom(
          ProcessRequestToProto(obj.process_request.value()));
      break;
    case vajra::RemoteInferenceRequest::Type::ABORT:
      ASSERT_VALID_RUNTIME(obj.abort_request.has_value(),
                           "Invalid value for abort_request");
      proto.mutable_abort_request()->CopyFrom(
          AbortRequestToProto(obj.abort_request.value()));
      break;
    case vajra::RemoteInferenceRequest::Type::STARTUP:
      ASSERT_VALID_RUNTIME(obj.startup_request.has_value(),
                           "Invalid value for startup_request");
      proto.mutable_startup_request()->CopyFrom(
          StartupRequestToProto(obj.startup_request.value()));
      break;
    case vajra::RemoteInferenceRequest::Type::CONFIG:
      ASSERT_VALID_RUNTIME(obj.config_request.has_value(),
                           "Invalid value for config_request");
      proto.mutable_config_request()->CopyFrom(
          ConfigRequestToProto(obj.config_request.value()));
      break;
  }
  return proto;
}

vajra::RemoteInferenceRequest ProtoUtils::RemoteInferenceRequestFromProto(
    const vajra_proto::RemoteInferenceRequest& proto) {
  if (proto.has_process_request()) {
    return vajra::RemoteInferenceRequest(
        ProcessRequestFromProto(proto.process_request()));
  } else if (proto.has_abort_request()) {
    return vajra::RemoteInferenceRequest(
        AbortRequestFromProto(proto.abort_request()));
  } else if (proto.has_startup_request()) {
    return vajra::RemoteInferenceRequest(
        StartupRequestFromProto(proto.startup_request()));
  } else if (proto.has_config_request()) {
    return vajra::RemoteInferenceRequest(
        ConfigRequestFromProto(proto.config_request()));
  } else {
    LOG_CRITICAL("RemoteInferenceRequest proto has no payload set");
    // Return a default request as a fallback
    return vajra::RemoteInferenceRequest(vajra::StartupRequest(false));
  }
}

//==============================================================================
// RemoteInferenceResponse conversion functions
//==============================================================================
vajra_proto::OutputResponse ProtoUtils::OutputResponseToProto(
    const vajra::OutputResponse& obj) {
  vajra_proto::OutputResponse proto;
  proto.set_request_id(obj.request_id);
  proto.set_text(obj.text);
  proto.mutable_token_ids()->Assign(obj.token_ids.begin(), obj.token_ids.end());
  proto.mutable_prompt_token_ids()->Assign(obj.prompt_token_ids.begin(),
                                           obj.prompt_token_ids.end());
  proto.set_finish_reason(obj.finish_reason);
  proto.set_finished(obj.finished);
  proto.set_is_delta(obj.is_delta);
  proto.set_is_first_chunk(obj.is_first_chunk);
  return proto;
}

vajra::OutputResponse ProtoUtils::OutputResponseFromProto(
    const vajra_proto::OutputResponse& proto) {
  std::vector<uint64_t> token_ids =
      ExtractRepeatedField<uint64_t>(proto.token_ids());
  std::vector<uint64_t> prompt_token_ids =
      ExtractRepeatedField<uint64_t>(proto.prompt_token_ids());

  return vajra::OutputResponse(
      proto.request_id(), proto.text(), std::move(token_ids),
      std::move(prompt_token_ids), proto.finish_reason(), proto.finished(),
      proto.is_delta(), proto.is_first_chunk());
}

vajra_proto::ErrorResponse ProtoUtils::ErrorResponseToProto(
    const vajra::ErrorResponse& obj) {
  vajra_proto::ErrorResponse proto;
  proto.set_request_id(obj.request_id);
  proto.set_error_message(obj.error_message);
  return proto;
}

vajra::ErrorResponse ProtoUtils::ErrorResponseFromProto(
    const vajra_proto::ErrorResponse& proto) {
  return vajra::ErrorResponse(proto.request_id(), proto.error_message());
}

vajra_proto::StartupResponse ProtoUtils::StartupResponseToProto(
    const vajra::StartupResponse& obj) {
  vajra_proto::StartupResponse proto;
  proto.set_server_ready(obj.server_ready);
  return proto;
}

vajra::StartupResponse ProtoUtils::StartupResponseFromProto(
    const vajra_proto::StartupResponse& proto) {
  return vajra::StartupResponse(proto.server_ready());
}

vajra_proto::RemoteInferenceResponse ProtoUtils::RemoteInferenceResponseToProto(
    const vajra::RemoteInferenceResponse& obj) {
  vajra_proto::RemoteInferenceResponse proto;
  switch (obj.type) {
    case vajra::RemoteInferenceResponse::Type::OUTPUT:
      ASSERT_VALID_RUNTIME(obj.output_response.has_value(),
                           "Invalid value for output_response");
      proto.mutable_request_output()->CopyFrom(
          OutputResponseToProto(obj.output_response.value()));
      break;
    case vajra::RemoteInferenceResponse::Type::ERROR:
      ASSERT_VALID_RUNTIME(obj.error_response.has_value(),
                           "Invalid value for error_response");
      proto.mutable_error()->CopyFrom(
          ErrorResponseToProto(obj.error_response.value()));
      break;
    case vajra::RemoteInferenceResponse::Type::STARTUP:
      ASSERT_VALID_RUNTIME(obj.startup_response.has_value(),
                           "Invalid value for startup_response");
      proto.mutable_startup_response()->CopyFrom(
          StartupResponseToProto(obj.startup_response.value()));
      break;
    case vajra::RemoteInferenceResponse::Type::MODEL_CONFIG:
      ASSERT_VALID_RUNTIME(obj.model_config.has_value(),
                           "Invalid value for model_config");
      proto.mutable_model_config()->CopyFrom(
          ModelConfigToProto(obj.model_config.value()));
      break;
  }
  return proto;
}

vajra::RemoteInferenceResponse ProtoUtils::RemoteInferenceResponseFromProto(
    const vajra_proto::RemoteInferenceResponse& proto) {
  if (proto.has_request_output()) {
    return vajra::RemoteInferenceResponse(
        OutputResponseFromProto(proto.request_output()));
  } else if (proto.has_error()) {
    return vajra::RemoteInferenceResponse(
        ErrorResponseFromProto(proto.error()));
  } else if (proto.has_startup_response()) {
    return vajra::RemoteInferenceResponse(
        StartupResponseFromProto(proto.startup_response()));
  } else if (proto.has_model_config()) {
    return vajra::RemoteInferenceResponse(
        ModelConfigFromProto(proto.model_config()));
  } else {
    LOG_CRITICAL("RemoteInferenceResponse proto has no payload set");
    // Return a default response as a fallback
    return vajra::RemoteInferenceResponse(vajra::StartupResponse(false));
  }
}
//==============================================================================
}  // namespace vajra
//==============================================================================
