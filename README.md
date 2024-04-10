# Interactive Tool for Performance Bound Calculation in TSN and Non-TSN Networks
The Network Performance Bounds Analyzer provides methods to create a visual representation of a network, generate random
networks, calculate
end-to-end delay and backlog bounds, and plot results.
Currently, we support two TSN models (Credit Based Shaper ([CBS]) and CBS with Control-Data Traffic
(CDT) and Asynchronous Traffic Shaper ([ATS])), and a machine learning approach based on [DeepTMA].
It runs on macOS, Windows, and Linux.
<img width="1850" alt="screenshot" src="https://github.com/Moni5656/npba/assets/54207942/11117a0c-f732-42bc-bfb7-6e8a79372b82">

## Installation

* [MATLAB] R2022b

* [RTC Toolbox]
* [.NET] Runtime 7.0
* Java Runtime Environment >=19
* Install dependencies:

```console
pip install networkx
pip install matplotlib
pip install scienceplots
pip install pythonnet
pip install matlabengine
pip install customtkinter
pip install pyyaml
pip install torch torchvision torchaudio
pip install torch-scatter -f https://data.pyg.org/whl/torch-1.13.0+cpu.html
pip install torch-sparse -f https://data.pyg.org/whl/torch-1.13.0+cpu.html
pip install torch-geometric
pip install gitpython
pip install torch==1.13.1
pip install tqdm
pip install scikit-learn
pip install gitpython
```

* For Linux users:
  * Install dependencies (in case they are not installed):
  ```console
    sudo apt install idle3
    sudo apt install python3-pil.imagetk
    ```

* For Windows and macOS users:
  * install [Latex] (required for scienceplots)
  * install [GhostScript] (optional)
  * install [Inkscape] (optional)

[CBS]: https://dl.acm.org/doi/abs/10.1145/2659787.2659810

[ATS]: https://arxiv.org/pdf/1804.10608.pdf

[DeepTMA]: https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/geyer2019infocom.pdf

[.NET]: https://dotnet.microsoft.com/en-us/download/dotnet/7.0

[RTC Toolbox]: https://www.mpa.ethz.ch/#mozTocId588080

[MATLAB]: https://www.mathworks.com/products/matlab.html

[Inkscape]: https://inkscape.org/de/

[Ghostscript]: https://www.ghostscript.com

[Latex]: https://github.com/garrettj403/SciencePlots/wiki/FAQ#installing-latex

## References

This project references and uses the following works:

* Wandeler E, Thiele L. 
  _Real-Time Calculus (RTC) Toolbox_.
  http://www.mpa.ethz.ch, 2008.

* R. Queck. 
  _Analysis of Ethernet AVB for automotive networks using network calculus_. 
  In Proc. of IEEE Int. Conf. on Vehicular Electronics and Safety(ICVES 2012). 
  IEEE, 2012.
  https://doi.org/10.1109/ICVES.2012.6294261

* J. A. R. De Azua and M. Boyer. 
 _Complete modelling of AVB in network calculus framework_. 
 In Proceedings of the 22nd International Conference on Real-Time Networks and Systems. Versaille, France: ACM Press, Oct. 2014, pp. 55-64.
 https://doi.org/10.1145/2659787.2659810

* E. Mohammadpour, E. Stai, M. Mohiuddin, and J.-Y. Le Boudec. 
  _Latency and Backlog Bounds in Time-Sensitive Networking with Credit Based Shapers and Asynchronous Traffic Shaping_. 
  In 2018 30th International Teletraffic Congress (ITC 30), volume 2, pages 1–6. IEEE, 2018.
  https://doi.org/10.1109/ITC30.2018.10053

* R. Zippo and G. Stea.
  _Nancy: An efficient parallel Network Calculus library_.
  In SoftwareX, Volume 19. Elsevier, 2022.
  https://doi.org/10.1016/j.softx.2022.101178
