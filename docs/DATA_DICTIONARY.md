# Data dictionary

The release preserves source column names. Missing values may be encoded as blank, `not_reported`, `unclear`, `unknown`, or `not_applicable`; none is equivalent to score zero.

## field_project_validation_matrix_sanitized.csv

`matrix_row_id`, `project_group`, `project_or_experiment`, `project_type`, `source_paper_id`, `source_title`, `source_authors`, `source_year`, `source_venue`, `source_doi_or_url`, `source_universe`, `evidence_role`, `field_evidence_subtype`, `primary_ml_workflow_evaluated_against_field_observations`, `counts_as_primary_ml_field_validation`, `monitoring_modality`, `geological_lesson`, `ml_use`, `validation_role`, `limitation`, `wp5_package_ids`, `data_regime`, `field_validation_category`, `controlled_release_validation_state`, `author_verified_override_used`, `role_boundary_statement`

## Fig01_plot_data.csv

`element_type`, `order`, `label`, `description`

## Fig02_plot_data.csv

`application_group`, `data_regime`, `N`

## Fig03_plot_data.csv

`dimension`, `category`, `N`

## Fig04_plot_data.csv

`application_group`, `outcome`, `outcome_label`, `total_N`, `positive_n`, `positive_fraction_total`, `not_reported_n`, `unclear_n`

## Fig05_plot_data.csv

`project_group`, `primary_ml_validation_count`, `field_or_mechanism_background_count`, `benchmark_design_anchor_count`, `source_paper_ids`, `total_relations`

## FIGURE_TRACEABILITY.csv

`figure_id`, `visual_element`, `aggregation_rule`, `source_file`, `source_paper_ids`, `source_paper_count`, `unknown_count`, `notes`

## full_text_verified_primary_core_sanitized.csv

`paper_id`, `title`, `authors`, `year`, `venue`, `doi_or_url`, `peer_review_status`, `storage_stage`, `application_area`, `application_group`, `decision_supported`, `data_regime`, `field_case`, `ml_method_family`, `target_outputs`, `validation_type`, `field_validation_category`, `controlled_release_validation_state`, `ood_test_category`, `cross_site_test_state`, `uncertainty_calibration_category`, `surrogate_error_propagation_category`, `mass_conservation_diagnostic`, `pressure_threshold_diagnostic`, `plume_volume_diagnostic`, `geomechanics_diagnostic`, `geochemistry_diagnostic`, `rock_physics_diagnostic`, `sensor_physics_diagnostic`, `field_evidence_score_state`, `physical_consistency_score_state`, `uncertainty_score_state`, `transferability_score_state`, `decision_readiness_score_state`, `wp4_main_claim_eligible`

## Table01_review_positioning.csv

`review`, `scope`, `decision_centered`, `sim_to_real_or_deployment`, `missingness_aware_verified_corpus`, `decision_specific_minimum_evidence`, `mrv_and_stewardship_auditability`, `open_traceability`, `positioning_implication`

## Table02_core_evidence_summary.csv

`application_group`, `N`, `dominant_evidence_regime`, `field_evaluation`, `controlled_event`, `OOD`, `cross_site_or_setting`, `calibrated_UQ_or_posterior`, `physical_diagnostic`, `surrogate_error_propagation`, `main_evidence_gap`

## Table03_minimum_validation_packages.csv

`package_id`, `storage_decision`, `hidden_variable_or_risk`, `current_verified_status`, `current_evidence_gap`, `claim_boundary`, `minimum_validation_logic`

## Table04_field_anchor_implications.csv

`project_group`, `project_or_experiment_names`, `evidence_roles`, `validation_implication`, `main_limitation`, `source_paper_ids`

## TABLE_TRACEABILITY.csv

`table_id`, `source_file`, `source_paper_ids`, `source_count`

## TableS01_main_claim_eligible_core.csv

`paper_id`, `title`, `authors`, `year`, `venue`, `doi_or_url`, `peer_review_status`, `storage_stage`, `application_area`, `application_group`, `decision_supported`, `data_regime`, `field_case`, `ml_method_family`, `target_outputs`, `validation_type`, `field_validation_category`, `controlled_release_validation_state`, `ood_test_category`, `cross_site_test_state`, `uncertainty_calibration_category`, `surrogate_error_propagation_category`, `mass_conservation_diagnostic`, `pressure_threshold_diagnostic`, `plume_volume_diagnostic`, `geomechanics_diagnostic`, `geochemistry_diagnostic`, `rock_physics_diagnostic`, `sensor_physics_diagnostic`, `field_evidence_score_state`, `physical_consistency_score_state`, `uncertainty_score_state`, `transferability_score_state`, `decision_readiness_score_state`, `wp4_main_claim_eligible`

## TableS02_decision_evidence_profiles.csv

`analysis_version`, `analysis_status`, `universe`, `application_group`, `dimension`, `total_N`, `available_n`, `score_0_n`, `score_1_n`, `score_2_n`, `score_3_n`, `score_4_n`, `score_ge3_n`, `score_ge3_proportion`, `score_ge3_wilson95_low`, `score_ge3_wilson95_high`, `median_score`, `unknown_n`, `not_reported_n`, `unclear_n`, `not_applicable_n`, `unscored_n`

## TableS03_validation_outcome_profiles.csv

`analysis_version`, `analysis_status`, `universe`, `application_group`, `outcome`, `source_field`, `total_N`, `available_n`, `positive_n`, `positive_proportion`, `positive_fraction_of_total`, `available_fraction_of_total`, `wilson95_low`, `wilson95_high`, `unknown_n`, `not_reported_n`, `unclear_n`, `not_applicable_n`

## TableS04_minimum_validation_packages_full.csv

`package_id`, `storage_decision`, `claim_scope`, `hidden_variable_or_risk`, `minimum_data_provenance`, `minimum_geological_representativeness`, `minimum_physical_diagnostics`, `minimum_uncertainty_evidence`, `minimum_transfer_evidence`, `minimum_field_or_experimental_evidence`, `minimum_decision_metric`, `minimum_audit_record`, `failure_if_absent`, `current_verified_status`, `current_evidence_gap`, `primary_support_ids`, `background_anchor_ids`, `claim_boundary`, `relevant_manuscript_section`

## TableS05_field_anchor_summary.csv

`project_group`, `project_or_experiment_names`, `project_types`, `wp5_package_ids`, `monitoring_modalities`, `geological_lessons`, `primary_ml_validation_count`, `field_or_mechanism_background_count`, `benchmark_design_anchor_count`, `source_paper_ids`, `validation_implication`, `main_limitation`

## TableS06_figure_traceability.csv

`figure_id`, `visual_element`, `aggregation_rule`, `source_file`, `source_paper_ids`, `source_paper_count`, `unknown_count`, `notes`
