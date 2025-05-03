import xara
import numpy as np

class _SectionInterface:
    def __init__(self, shape, material):
        self._model = None
        self._material = material
        self._shape = shape


    def initialize(self):
        if self._model is not None:
            self._model.wipe()

        self._model = xara.Model(ndm=3, ndf=6)
        m = self._material
        self._model.nDMaterial(m["type"], 1, **{k: v for k, v in m.items() if k != "type"})

        self._model.section("ShearFiber", 1)
        for fiber in self._shape.create_fibers():
            self._model.fiber(**fiber, material=1, section=1)
        
        self._model.invoke("section", 1, ["update 0 0 0 0 0 0;"])


    def getStressResultant(self, e, commit=True):
        eps, kap = map(float, e)
        stress = self._model.invoke("section", 1, [
                        f"update  {eps} 0 0 0 0 {kap};",
                         "stress"
        ] + (["commit"] if commit else []))
        return np.array(stress)[[0, 5]]

    def getSectionTangent(self):
        tangent = self._model.invoke("section", 1, [
                        "tangent"
        ])

        n = int(np.sqrt(len(tangent)))
        Ks = np.round(np.array(tangent), 4).reshape(n,n)
        return Ks


def _solve_eps(sect, kap, axial: float, eps0, tol=1e-8, maxiter=15, time=0.0):
    # Newton-Raphson iteration
    eps = eps0
    s = sect.getStressResultant([eps, kap], False)
    for i in range(maxiter):
        if abs(s[0] - axial) < tol:
            return eps
        s = sect.getStressResultant([eps, kap], False)
        eps -= (s[0] - axial)/sect.getSectionTangent()[0,0]
    
    print(f"Warning: {maxiter} iterations reached, r = {s[0] - axial}, {time = }")
    return None

    return eps


def _analyze(s, P, dkap, nstep):
    s.initialize()
    k0 = 0.0

    kap = 0
    if eo := _solve_eps(s,  k0,  P,  0.0):
        e0 = _solve_eps(s,  k0,  P,  eo)
    else:
        e0 = 0.0

    PM = [
        s.getStressResultant([e0, k0], True)
    ]
    if e1 := _solve_eps(s, k0+dkap, P, e0):
        PM.append(s.getStressResultant([e1, k0+dkap], True))

        e = e0
        kap = 2*dkap
        for _ in range(nstep):
            # if abs(PM[-1][1]) < 0.995*abs(PM[-2][1]):
            #     break
            e = _solve_eps(s, kap, P, e)
            if e is None:
                break
            PM.append(s.getStressResultant([e, kap], True))
            kap += dkap
    return PM, kap


class SectionInteraction:
    def __init__(self, section, axial):
        self.axial = axial
        self.section = _SectionInterface(*section)

    def analyze(self, nstep = 30, incr=5e-6):
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots(1,2, sharey=True, constrained_layout=True)
        sect = self.section
        axial = self.axial


        # Curvature increment
        dkap = incr
        s = sect
        for P in axial:
            PM, kmax = _analyze(s, P, dkap, nstep)

            p, m = zip(*PM)

            ax[0].scatter(np.linspace(0.0, kmax, len(m)), m, s=0.2)

            ax[1].scatter(p, m, s=0.2)#, color="k")

        ax[0].set_xlabel("Curvature, $\\kappa$")
        ax[0].set_ylabel("Moment, $M(\\varepsilon, \\kappa)$")
        ax[1].set_xlabel("Axial force, $P$")
        # ax[1].set_ylabel("Moment, $M$")

        # plt.show()

