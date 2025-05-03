from xsection import ElasticConstants
from dataclasses import dataclass
from collections.abc import Mapping


from ._patch import (
      _patch as patch,
      layer,
      SectionGeometry
)

class Mesh:
    nodes: list
    elems: list

class Material:
    pass 


class WarpingSection:

    def __init__(self, model: "TriangleModel",
                 warp_twist=True, 
                 warp_shear=True
        ):

        self._w_model = model

        self._warp_shear:bool = warp_shear
        self._warp_twist:bool = warp_twist

    #
    # Virtual
    #
    @property
    def model(self):
        if self._w_model is None:
            raise ValueError("Model not initialized")
        return self._w_model

    @property
    def _analysis(self):
        from .solvers import TorsionAnalysis
        if not hasattr(self, "_warp_analysis") or self._warp_analysis is None:
            self._warp_analysis = TorsionAnalysis(self.model)
        
        return self._warp_analysis 

    #
    # Final
    #
    @classmethod
    def from_meshio(cls, mesh, **kwds):
        from .solvers import TriangleModel
        return WarpingSection(TriangleModel.from_meshio(mesh), **kwds)

    def exterior(self):
        return self._w_model.exterior()

    def interior(self):
        return self._w_model.interior()
    
    @property
    def centroid(self):
        return self._analysis.centroid()

    def torsion_warping(self):
        return self._analysis.warping()

    def summary(self, symbols=False, format=None):
        s = ""
        tol=1e-13
        A = self._analysis.cnn()[0,0]

        cnw = self._analysis.cnw()
        cnm = self._analysis.cnm()
        Ay = cnm[0,1] # int z
        Az = cnm[2,0] # int y
        # Compute centroid
        cx, cy = float(Az/A), float(Ay/A)
        cx, cy = map(lambda i: i if abs(i)>tol else 0.0, (cx, cy))

        cmm = self._analysis.cmm()
        cmw = self._analysis.cmw()
        cnv = self._analysis.cnv()

        Ivv = self._analysis.cvv()[0,0]
        cmv = self._analysis.cmv()
        # Irw = self.torsion.cmv()[0,0]

        sx, sy = self._analysis.shear_center()
        sx, sy = map(lambda i: i if abs(i)>tol else 0.0, (sx, sy))

        cww = self._analysis.cww()
        # Translate to shear center to get standard Iww
        Iww = self.translate([sx, sy])._analysis.cww()[0,0]

        Isv = self._analysis.torsion_constant()

        s += f"""
  [nn]    Area               {A          :>10.4}
  [nm]    Centroid           {0.0        :>10.4}  {cx         :>10.4}, {cy         :>10.4}
  [nw|v]                     {cnw[0,0]/A :>10.4}  {cnv[1,0]/A :>10.4}, {cnv[2,0]/A :>10.4}

  [mm]    Flexural moments   {cmm[0,0]   :>10.4}  {cmm[1,1]   :>10.4}, {cmm[2,2]   :>10.4}, {cmm[1,2] :>10.4}
  [mv|w]                     {cmv[0,0]   :>10.4}  {cmw[1,0]   :>10.4}, {cmw[2,0]   :>10.4}

          Shear center       {0.0        :>10.4}  {sx         :>10.4}, {sy :>10.4}

  [ww]    Warping constant   {cww[0,0] :>10.4}  ({Iww      :>10.4} at S.C.)
          Torsion constant   {Isv :>10.4}
  [vv]    Bishear            {Ivv :>10.4}
        """

        return s

    def translate(self, offset):
        # TODO: translate fibers
        return WarpingSection(self._w_model.translate(offset)) 

    def rotate(self, angle):
        # TODO: rotate fibers
        return WarpingSection(self._w_model.rotate(angle)) 


    def linspace(self, start, stop, num, radius=None, **kwds):
        import numpy as np
        if radius is None:
            for x in np.linspace(start, stop, num=num):
                yield self.translate(x-self.centroid, **kwds)

    @property
    def elastic(self)->ElasticConstants:
        import numpy as np
        y, z = self._w_model.nodes.T
        e = np.ones(y.shape)
        return ElasticConstants(
            A  =self._w_model.inertia(e, e),
            Iyz=self._w_model.inertia(y, z),
            Iy =self._w_model.inertia(z, z),
            Iz =self._w_model.inertia(y, y)
        )

    def integrate(self, f: callable):
        pass

    def create_fibers(self, *args, **kwds):
        yield from self.fibers(*args, **kwds)

    def fibers(self, origin=None, center=None, types=None, material=None):
        """
        use material to force a homogeneous material
        """

        if origin is not None:
            if origin == "centroid":
                yield from self.translate(self._analysis.centroid()).fibers(center=center)
            elif origin == "shear-center":
                yield from self.translate(self._analysis.shear_center()).fibers(center=center)
            else:
                yield from self.translate(origin).fibers(center=center)
            return

        # for fiber in self._point_fibers:
        #     yield fiber

        model = self.model

        if center is None:
            twist = self._analysis
            w = self._analysis.solution() #warping() # 
        elif not isinstance(center, str):
            twist = self.translate(center)._analysis
            w = twist.solution()
        elif center == "centroid":
            twist = self.translate(self._analysis.centroid())._analysis
            w = twist.solution()
        elif center == "shear-center":
            w = self._analysis.warping()
            twist = self._analysis


        # if callable(self._warp_shear):
        #     psi = self._warp_shear
        # else:
        psi = lambda y,z: 0.0

        for i,elem in enumerate(self.model.elems):
            # TODO: Assumes TriangleModel
            yz = sum(model.nodes[elem.nodes])/3
            fiber = dict(
                y=yz[0],
                z=yz[1],
                area=model.cell_area(i),
                warp=[
                    [twist.model.cell_solution(i, w), *twist.model.cell_gradient(i,  w)],
                    [0, psi(*yz), 0]
                ]
            )
            if material is not None:
                fiber["material"] = material

            yield fiber

    def _repr_html_(self):
        import veux
        from veux.viewer import Viewer
        m = self.model
        a = veux.create_artist((m.nodes, m.cells()), ndf=1)
        a.draw_surfaces()
        viewer = Viewer(a,hosted=False,standalone=False)
        html = viewer.get_html()
        return html

GeneralSection = WarpingSection
