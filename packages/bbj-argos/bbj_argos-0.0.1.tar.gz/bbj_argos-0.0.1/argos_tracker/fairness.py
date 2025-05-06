from equalityml import FAIR

def fairness_metric(X_train, y_train, model, protected_variable, metric_name='statistical_parity_ratio', privileged_class=1):
  training_data = X_train.copy()
  training_data['Y'] = y_train
  
  # Available fairness metrics are: 
  # 1. 'treatment_equality_ratio'
  # 2. 'treatment_equality_difference'
  # 3. 'balance_positive_class': Balance for positive class
  # 4. 'balance_negative_class': Balance for negative class
  # 5. 'equal_opportunity_ratio': Equal opportunity ratio
  # 6. 'accuracy_equality_ratio': Accuracy equality ratio
  # 7. 'predictive_parity_ratio':  Predictive parity ratio
  # 8. 'predictive_equality_ratio': Predictive equality ratio
  # 9. 'statistical_parity_ratio': Statistical parity ratio
    
  # Instantiate a FAIR object
  fair_obj = FAIR(
    ml_model=model, 
    training_data=training_data,
    target_variable='Y',
    protected_variable=protected_variable, 
    privileged_class=privileged_class
  )
  # Evaluate fairness
  fairness_metric = fair_obj.fairness_metric(metric_name)
  return fairness_metric

def fairness_metrics(X_train, y_train, model, protected_variables, threshold):
  training_data = X_train.copy()
  training_data['Y'] = y_train
  
  options = [
    'treatment_equality_ratio',
    'treatment_equality_difference',
    'balance_positive_class',         # Balance for positive class
    'balance_negative_class',         # Balance for negative class
    'equal_opportunity_ratio',        # Equal opportunity ratio
    'accuracy_equality_ratio',        # Accuracy equality ratio
    'predictive_parity_ratio',        # Predictive parity ratio
    'statistical_parity_ratio'        # Statistical parity ratio
  ]

  metrics = {}
  for protected_variable in protected_variables:
    for metric in options:
      name = protected_variable['name']
      reference_group = protected_variable['reference_group']
      metrics[f'{_to_camel_case(name)}_{metric}'] = fairness_metric(X_train, y_train, model, name, metric_name=metric, privileged_class=reference_group)

  return metrics

# def fairness_metrics(X_train, y_train, model, protected_variables, privileged_class=1):
#   training_data = X_train.copy()
#   training_data['Y'] = y_train
  
#   options = [
#     'treatment_equality_ratio',
#     'treatment_equality_difference',
#     'balance_positive_class',         # Balance for positive class
#     'balance_negative_class',         # Balance for negative class
#     'equal_opportunity_ratio',        # Equal opportunity ratio
#     'accuracy_equality_ratio',        # Accuracy equality ratio
#     'predictive_parity_ratio',        # Predictive parity ratio
#     'statistical_parity_ratio'        # Statistical parity ratio
#   ]

#   metrics = {}
#   for protected_variable in protected_variables:
#     for metric in options:
#       metrics[f'{_to_camel_case(protected_variable)}_{metric}'] = fairness_metric(X_train, y_train, model, protected_variable, metric_name=metric, privileged_class=privileged_class)

#   return metrics

def _to_camel_case(text):
    s = text.replace("-", " ").replace("_", " ")
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + ''.join(i.capitalize() for i in s[1:])

