#pragma once
#include <zmq.hpp>
#include "action.hh"
#include "capability.hh"

namespace ghidra {

class ActionFactory;

class ReOxide : public CapabilityPoint, public UniversalActionHook {
 private:
  zmq::context_t ctx;
  zmq::socket_t sock;
  std::unique_ptr<ActionFactory> action_factory;

 public:
  ReOxide();
  ~ReOxide();

  void initialize(void) override;
  void send_string(const string& s);
  void universalAction(Architecture* conf, ActionGroup* action) override;
};

}  // End namespace ghidra
