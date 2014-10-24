// Protocol Buffers - Google's data interchange format
// Copyright 2008 Google Inc.  All rights reserved.
// http://code.google.com/p/protobuf/
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//     * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//     * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// Author: kenton@google.com (Kenton Varda)
//  Based on original Protocol Buffers design by
//  Sanjay Ghemawat, Jeff Dean, and others.

#include <google/protobuf/unknown_field_set.h>
#include <google/protobuf/stubs/stl_util-inl.h>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/wire_format.h>

namespace google {
namespace protobuf {

UnknownFieldSet::UnknownFieldSet()
  : internal_(NULL) {}

UnknownFieldSet::~UnknownFieldSet() {
  if (internal_ != NULL) {
    STLDeleteValues(&internal_->fields_);
    delete internal_;
  }
}

void UnknownFieldSet::Clear() {
  if (internal_ == NULL) return;

  if (internal_->fields_.size() > kMaxInactiveFields) {
    STLDeleteValues(&internal_->fields_);
  } else {
    // Don't delete the UnknownField objects.  Just remove them from the active
    // set.
    for (int i = 0; i < internal_->active_fields_.size(); i++) {
      internal_->active_fields_[i]->Clear();
      internal_->active_fields_[i]->index_ = -1;
    }
  }

  internal_->active_fields_.clear();
}

void UnknownFieldSet::MergeFrom(const UnknownFieldSet& other) {
  for (int i = 0; i < other.field_count(); i++) {
    AddField(other.field(i).number())->MergeFrom(other.field(i));
  }
}

bool UnknownFieldSet::MergeFromCodedStream(io::CodedInputStream* input) {

  UnknownFieldSet other;
  if (internal::WireFormat::SkipMessage(input, &other) &&
                                  input->ConsumedEntireMessage()) {
    MergeFrom(other);
    return true;
  } else {
    return false;
  }
}

bool UnknownFieldSet::ParseFromCodedStream(io::CodedInputStream* input) {
  Clear();
  return MergeFromCodedStream(input);
}

bool UnknownFieldSet::ParseFromZeroCopyStream(io::ZeroCopyInputStream* input) {
  io::CodedInputStream coded_input(input);
  return ParseFromCodedStream(&coded_input) &&
    coded_input.ConsumedEntireMessage();
}

bool UnknownFieldSet::ParseFromArray(const void* data, int size) {
  io::ArrayInputStream input(data, size);
  return ParseFromZeroCopyStream(&input);
}

const UnknownField* UnknownFieldSet::FindFieldByNumber(int number) const {
  if (internal_ == NULL) return NULL;

  map<int, UnknownField*>::iterator iter = internal_->fields_.find(number);
  if (iter != internal_->fields_.end() && iter->second->index() != -1) {
    return iter->second;
  } else {
    return NULL;
  }
}

UnknownField* UnknownFieldSet::AddField(int number) {
  if (internal_ == NULL) internal_ = new Internal;

  UnknownField** map_slot = &internal_->fields_[number];
  if (*map_slot == NULL) {
    *map_slot = new UnknownField(number);
  }

  UnknownField* field = *map_slot;
  if (field->index() == -1) {
    field->index_ = internal_->active_fields_.size();
    internal_->active_fields_.push_back(field);
  }
  return field;
}

int UnknownFieldSet::SpaceUsedExcludingSelf() const {
  int total_size = 0;
  if (internal_ != NULL) {
    total_size += sizeof(*internal_);
    total_size += internal_->active_fields_.capacity() *
                  sizeof(Internal::FieldVector::value_type);
    total_size += internal_->fields_.size() *
        sizeof(Internal::FieldMap::value_type);

    // Account for the UnknownField objects themselves.
    for (Internal::FieldMap::const_iterator it = internal_->fields_.begin(),
         end = internal_->fields_.end();
         it != end;
         ++it) {
      total_size += it->second->SpaceUsed();
    }
  }
  return total_size;
}

int UnknownFieldSet::SpaceUsed() const {
  return sizeof(*this) + SpaceUsedExcludingSelf();
}

UnknownField::UnknownField(int number)
  : number_(number),
    index_(-1) {
}

UnknownField::~UnknownField() {
}

void UnknownField::Clear() {
  clear_varint();
  clear_fixed32();
  clear_fixed64();
  clear_length_delimited();
  clear_group();
}

void UnknownField::MergeFrom(const UnknownField& other) {
  varint_          .MergeFrom(other.varint_          );
  fixed32_         .MergeFrom(other.fixed32_         );
  fixed64_         .MergeFrom(other.fixed64_         );
  length_delimited_.MergeFrom(other.length_delimited_);
  group_           .MergeFrom(other.group_           );
}

int UnknownField::SpaceUsed() const {
  int total_size = sizeof(*this);
  total_size += varint_.SpaceUsedExcludingSelf();
  total_size += fixed32_.SpaceUsedExcludingSelf();
  total_size += fixed64_.SpaceUsedExcludingSelf();
  total_size += length_delimited_.SpaceUsedExcludingSelf();
  total_size += group_.SpaceUsedExcludingSelf();
  return total_size;
}

}  // namespace protobuf
}  // namespace google
