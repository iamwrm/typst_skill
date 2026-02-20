#import "template.typ": conf, theorem, definition, remark

#show: conf.with(
  title: "傅里叶变换与信号处理基础",
  title-en: "Fourier Transform and Fundamentals of Signal Processing",
  authors: (
    (name: "王志远", id: "1"),
    (name: "李思涵", id: "1"),
  ),
  affiliations: (
    (id: "1", text: "清华大学电子工程系，北京 100084"),
  ),
  abstract-zh: [
    傅里叶变换是现代信号处理与数学分析的核心工具之一。本文系统地介绍了连续傅里叶变换、逆变换、卷积定理、帕塞瓦尔定理以及离散傅里叶变换的基本理论，并给出常见变换对的对照表，为读者提供信号处理领域的理论基础。
  ],
  abstract-en: [
    The Fourier transform is one of the central tools in modern signal processing and mathematical analysis. This paper systematically introduces the continuous Fourier transform, its inverse, the convolution theorem, Parseval's theorem, and the discrete Fourier transform, along with a reference table of common transform pairs.
  ],
  keywords: ("傅里叶变换", "信号处理", "卷积定理", "帕塞瓦尔定理", "离散傅里叶变换"),
  lang: "zh",
)

= 引言

傅里叶分析是数学和工程学中最深刻、最有影响力的理论之一。1807年，法国数学家让·巴蒂斯特·约瑟夫·傅里叶（Jean-Baptiste Joseph Fourier）在研究热传导问题时提出：任意周期函数都可以表示为三角函数（正弦与余弦）的无穷级数之和。这一思想后来发展为傅里叶变换理论，成为信号处理、量子力学、图像处理、通信工程等众多领域的基石。

本文的主要目的是为读者提供傅里叶变换的数学基础与信号处理应用的入门指导。文章首先定义连续傅里叶变换及其逆变换，随后讨论关键性质与定理，最后引入离散傅里叶变换并给出常见变换对的参考表格。

= 连续傅里叶变换

== 基本定义

#definition[定义 1（傅里叶变换）][
  设 $f(t)$ 为绝对可积函数，即 $integral_(-infinity)^(infinity) abs(f(t)) dif t < infinity$，则其傅里叶变换定义为：
  $ hat(f)(omega) = cal(F){f(t)} = integral_(-infinity)^(infinity) f(t) e^(-j omega t) dif t $
  其中 $omega$ 为角频率，$j = sqrt(-1)$ 为虚数单位。函数 $hat(f)(omega)$ 也称为 $f(t)$ 的频谱函数。
]

上述定义将时域信号 $f(t)$ 映射到频域表示 $hat(f)(omega)$，揭示了信号中各频率分量的幅度与相位信息。这一变换是线性算子，即对于常数 $a, b$ 和函数 $f, g$，有：

$ cal(F){a f(t) + b g(t)} = a cal(F){f(t)} + b cal(F){g(t)} $

== 傅里叶逆变换

#definition[定义 2（傅里叶逆变换）][
  若 $hat(f)(omega)$ 为 $f(t)$ 的傅里叶变换，则原函数可通过逆变换恢复：
  $ f(t) = cal(F)^(-1){hat(f)(omega)} = frac(1, 2 pi) integral_(-infinity)^(infinity) hat(f)(omega) e^(j omega t) dif omega $
  该公式表明时域函数与频域函数之间存在一一对应关系。
]

傅里叶变换与逆变换构成一对互逆运算。条件是 $f(t)$ 满足狄利克雷（Dirichlet）条件：在任何有限区间上，$f(t)$ 只有有限个间断点和有限个极值点。

#remark[注记 1][
  在工程实践中，常采用频率 $f$（单位：Hz）代替角频率 $omega$（单位：rad/s），此时变换对变为：
  $ hat(f)(nu) = integral_(-infinity)^(infinity) f(t) e^(-j 2 pi nu t) dif t, quad f(t) = integral_(-infinity)^(infinity) hat(f)(nu) e^(j 2 pi nu t) dif nu $
  两种形式在数学上等价，仅系数分配不同。本文统一采用角频率形式。
]

= 基本性质与重要定理

== 卷积定理

卷积运算是线性系统理论的核心概念。两个信号的卷积在频域中变为简单的乘法运算，这使得频域分析具有极大的计算优势。

#definition[定义 3（卷积）][
  两个函数 $f(t)$ 和 $g(t)$ 的卷积定义为：
  $ (f * g)(t) = integral_(-infinity)^(infinity) f(tau) g(t - tau) dif tau $
]

#theorem[定理 1（时域卷积定理）][
  若 $cal(F){f(t)} = hat(f)(omega)$，$cal(F){g(t)} = hat(g)(omega)$，则：
  $ cal(F){f * g} = hat(f)(omega) dot hat(g)(omega) $
  即时域中的卷积等价于频域中的逐点乘积。
]

#theorem[定理 2（频域卷积定理）][
  对偶地，时域中的乘积对应频域中的卷积（带缩放因子）：
  $ cal(F){f(t) dot g(t)} = frac(1, 2 pi) hat(f)(omega) * hat(g)(omega) $
]

卷积定理的重要意义在于：对于线性时不变（LTI）系统，输出信号 $y(t)$ 可以表示为输入信号 $x(t)$ 与系统冲激响应 $h(t)$ 的卷积：$y(t) = x(t) * h(t)$。在频域中，这等价于 $hat(y)(omega) = hat(x)(omega) dot hat(h)(omega)$，其中 $hat(h)(omega)$ 称为系统的传递函数。

== 帕塞瓦尔定理

#theorem[定理 3（帕塞瓦尔定理）][
  设 $f(t)$ 的傅里叶变换为 $hat(f)(omega)$，则信号的总能量在时域和频域中相等：
  $ integral_(-infinity)^(infinity) abs(f(t))^2 dif t = frac(1, 2 pi) integral_(-infinity)^(infinity) abs(hat(f)(omega))^2 dif omega $
  更一般地，对两个信号 $f(t)$ 和 $g(t)$，有：
  $ integral_(-infinity)^(infinity) f(t) overline(g(t)) dif t = frac(1, 2 pi) integral_(-infinity)^(infinity) hat(f)(omega) overline(hat(g)(omega)) dif omega $
]

#remark[注记 2][
  帕塞瓦尔定理也常被称为瑞利（Rayleigh）定理或能量守恒定理。它保证了从时域到频域的变换是一个保范映射（即 $L^2$ 等距同构），这在泛函分析和量子力学中具有深远意义。量 $abs(hat(f)(omega))^2$ 称为信号的能量谱密度或功率谱密度。
]

== 其他重要性质

傅里叶变换还具有以下常用性质。设 $cal(F){f(t)} = hat(f)(omega)$：

- *时移性质*：$cal(F){f(t - t_0)} = e^(-j omega t_0) hat(f)(omega)$，时域中的延迟等价于频域中乘以复指数。
- *频移性质*：$cal(F){e^(j omega_0 t) f(t)} = hat(f)(omega - omega_0)$，对应信号的调制操作。
- *尺度变换*：$cal(F){f(a t)} = frac(1, abs(a)) hat(f)(omega / a)$，时域压缩对应频域展宽。
- *微分性质*：$cal(F){f'(t)} = j omega hat(f)(omega)$，时域微分对应频域乘以 $j omega$。
- *对偶性*：若 $cal(F){f(t)} = hat(f)(omega)$，则 $cal(F){hat(f)(t)} = 2 pi f(-omega)$。

= 离散傅里叶变换

== DFT的定义

在实际的数字信号处理中，信号是离散采样的，因此需要离散傅里叶变换（DFT）。

#definition[定义 4（离散傅里叶变换）][
  对于长度为 $N$ 的离散序列 $x[n]$（$n = 0, 1, dots, N-1$），其DFT定义为：
  $ X[k] = sum_(n=0)^(N-1) x[n] e^(-j frac(2 pi, N) n k), quad k = 0, 1, dots, N-1 $
  对应的逆离散傅里叶变换（IDFT）为：
  $ x[n] = frac(1, N) sum_(k=0)^(N-1) X[k] e^(j frac(2 pi, N) n k), quad n = 0, 1, dots, N-1 $
]

令 $W_N = e^(-j 2 pi \/ N)$ 为 $N$ 次单位根，则DFT可以简洁地表示为 $X[k] = sum_(n=0)^(N-1) x[n] W_N^(n k)$。

#remark[注记 3][
  直接计算DFT的时间复杂度为 $O(N^2)$。1965年，库利（Cooley）和图基（Tukey）提出了快速傅里叶变换（FFT）算法，将计算复杂度降低到 $O(N log N)$，这使得DFT在实际工程中得以广泛应用。FFT是20世纪最重要的数值算法之一。
]

== 采样定理

#theorem[定理 4（奈奎斯特–香农采样定理）][
  设带限信号 $f(t)$ 的最高频率为 $f_max$，则当采样频率 $f_s >= 2 f_max$ 时，信号可以从其离散样本中无失真地完美重建：
  $ f(t) = sum_(n=-infinity)^(infinity) f[n] "sinc"(frac(f_s t - n, 1)) $
  其中 $"sinc"(x) = sin(pi x) \/ (pi x)$。频率 $f_N = 2 f_max$ 称为奈奎斯特频率。
]

采样定理是连续世界与离散世界之间的桥梁，也是模数转换（ADC）设计的理论基础。当采样频率低于奈奎斯特频率时，将产生频谱混叠（aliasing）现象，导致信号无法正确恢复。

= 常见傅里叶变换对

下表列出了若干常用的傅里叶变换对，供读者查阅参考。

#figure(
  table(
    columns: 3,
    align: (center, center, left),
    table.header[序号][时域信号 $f(t)$][频域 $hat(f)(omega)$],
    table.hline(stroke: 0.8pt),
    [1], [$delta(t)$（冲激函数）], [$1$],
    [2], [$1$（常数）], [$2 pi delta(omega)$],
    [3], [$e^(-a t) u(t), quad a > 0$], [$display(frac(1, a + j omega))$],
    [4], [$e^(-a abs(t)), quad a > 0$], [$display(frac(2a, a^2 + omega^2))$],
    [5], [$e^(-a t^2), quad a > 0$], [$display(sqrt(frac(pi, a)) e^(-omega^2 \/ (4a)))$],
    [6], [$cos(omega_0 t)$], [$pi[delta(omega - omega_0) + delta(omega + omega_0)]$],
    [7], [$sin(omega_0 t)$], [$display(frac(pi, j))[delta(omega - omega_0) - delta(omega + omega_0)]$],
    [8], [$"rect"(t\/T)$（矩形脉冲）], [$T "sinc"(omega T \/ 2)$],
    table.hline(stroke: 0.5pt),
  ),
  caption: [常见傅里叶变换对一览表（其中 $u(t)$ 为单位阶跃函数，$delta(t)$ 为狄拉克函数）],
)

#remark[注记 4][
  上表中第5行给出的高斯函数变换对特别重要：高斯函数的傅里叶变换仍为高斯函数。这一性质使得高斯函数成为不确定性原理（Heisenberg uncertainty principle）的等号成立情形，即在时频联合域中达到最优的"能量集中度"。
]

= 结论

本文从数学定义出发，系统阐述了傅里叶变换的核心理论框架。连续傅里叶变换建立了时域与频域之间的桥梁，卷积定理揭示了线性时不变系统的频域简化分析方法，帕塞瓦尔定理保证了能量在两个域中的守恒性。离散傅里叶变换及其快速算法（FFT）则使得数字信号处理成为可能。

傅里叶分析的应用远不止于此。在图像处理中，二维傅里叶变换用于频域滤波与图像压缩；在通信工程中，正交频分复用（OFDM）技术直接基于DFT/IDFT实现；在量子力学中，动量空间与位置空间的波函数通过傅里叶变换相互关联。掌握傅里叶变换的理论基础，对于深入理解上述应用领域至关重要。
