TrialBench: Multi-modal AI-ready Clinical Trial Datasets
====================================

.. image:: https://img.shields.io/pypi/v/trialbench.svg?color=brightgreen
   :target: https://pypi.org/project/trialbench/
   :alt: PyPI version

.. .. image:: https://readthedocs.org/projects/trialbench/badge/?version=latest
..    :target: https://trialbench.readthedocs.io/en/latest/
..    :alt: Documentation status

.. .. image:: https://static.pepy.tech/badge/trialbench
..    :target: https://pepy.tech/project/trialbench
..    :alt: Downloads

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

1. Installation :rocket:
----------------------------
```bash
pip install trialbench
```

2. Tasks & Phases :clipboard:
-------------------------------
Supported Tasks
| Task Type                      | Task Name                                 | Phase Name |
|--------------------------------|-------------------------------------------|-------------|
| Mortality Prediction           | `mortality_rate`/`mortality_rate_yn`      | 1-4 |
| Adverse Event Prediction       | `serious_adverse_rate`/`serious_adverse_rate_yn` | 1-4 |
| Patient Retention Prediction   | `patient_dropout_rate`/`patient_dropout_rate_yn` | 1-4 |
| Trial Duration Prediction      | `duration`                                | 1-4  |
| Trial Outcome Prediction       | `outcome`                                 | 1-4 |
| Trial Failure Analysis         | `failure_reason`                          | 1-4 |
| Dosage Prediction              | `dose`/`dose_cls`                         | all |

Clinical Trial Phases
```
Phase 1: Safety Evaluation
Phase 2: Efficacy Assessment
Phase 3: Large-scale Testing
Phase 4: Post-marketing Surveillance
```

3. Quick Start :zap:
---------------------
```python
import trialbench

# Load dataset
task = 'dose'
phase = 'all'
# Load data
train_loader, valid_loader, test_loader, num_classes, tabular_input_dim = trialbench.load_data(task, phase)

```

4. Data Loading :card_file_box:
--------------------------------
`load_data` Parameters
| Parameter | Type | Description | 
|-----------|------|-------------|
| `task`    | str  | Target prediction task (e.g., 'mortality_rate_yn') |
| `phase`   | int  | Clinical trial phase (1-4) |

Returns
| Object              | Type          | Description |
|---------------------|---------------|-------------|
| `train_loader`      | DataLoader    | Training set loader |
| `valid_loader`      | DataLoader    | Validation set loader |
| `test_loader`       | DataLoader    | Test set loader |
| `num_classes`       | int           | Number of output classes |
| `tabular_input_dim` | int           | Dimension of tabular features |

5. Citation :handshake:
------------------------
If you use TrialBench in your research, please cite:
```bibtex
@article{chen2024trialbench,
  title={Trialbench: Multi-modal artificial intelligence-ready clinical trial datasets},
  author={Chen, Jintai and Hu, Yaojun and Wang, Yue and Lu, Yingzhou and Cao, Xu and Lin, Miao and Xu, Hongxia and Wu, Jian and Xiao, Cao and Sun, Jimeng and others},
  journal={arXiv preprint arXiv:2407.00631},
  year={2024}
}
```

---


