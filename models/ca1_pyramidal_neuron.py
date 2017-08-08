"""


"""

from os.path import join
import sciunit
from neuronunit.capabilities import ReceivesSquareCurrent, ProducesMembranePotential, Runnable
from neuron import h, hclass
import neo
from quantities import ms


h.celsius = 34.0


class CA1PyramidalNeuron(sciunit.Model,
                         ReceivesSquareCurrent,
                         ProducesMembranePotential,
                         Runnable):
    def __init__(self, name=None, id=None, template="CCell", v_init=-80.0, celsius=34, version=None,
                 working_dir="."):
        sciunit.Model.__init__(self, name=name)
        h.nrn_load_dll(join(working_dir, "mechanisms/x86_64/.libs/libnrnmech.so"))
        h.load_file(join(working_dir, "checkpoints/cell.hoc"))
        self.id = id
        self.version = version
        self.working_dir = working_dir
        h.v_init = v_init
        h.celsius = celsius
        self.cell = getattr(h, template)(join(working_dir, "morphology"))
        self.iclamp = h.IClamp(0.5, sec=self.cell.soma[0])
        self.vm = h.Vector()
        self.vm.record(self.cell.soma[0](0.5)._ref_v)

    def get_membrane_potential(self):
        """Must return a neo.AnalogSignal."""
        signal = neo.AnalogSignal(self.vm,
                                  units="mV",
                                  sampling_period=h.dt * ms)
        return signal

    def inject_current(self, current):
        """
        Injects somatic current into the model.

        Parameters
        ----------
        current : a dictionary like:
                      {'amplitude':-10.0*pq.pA,
                       'delay':100*pq.ms,
                       'duration':500*pq.ms}}
                  where 'pq' is the quantities package
        """
        self.iclamp.amp = current["amplitude"]
        self.iclamp.delay = current["delay"]
        self.iclamp.dur = current["duration"]

    def run(self, tstop):
        t_alert = 100.0
        h.check_simulator()
        h.cvode.active(0)
        self.vm.resize(0)
        h.finitialize(h.v_init)
        while h.t < tstop:
            h.fadvance()
            if h.t > t_alert:
                print("Time: {} ms".format(t_alert))
                t_alert += 100.0
