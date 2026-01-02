# Libre LIMS - Guías de Desarrollo

## Django Views
- **SIEMPRE usar class-based views (CBVs)**
- No usar function-based views (FBVs)
- Usar generic views de Django: ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
- Usar mixins para funcionalidad reutilizable (LoginRequiredMixin, etc.)

## Patrón de Views Preferido

```python
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class MyModelListView(LoginRequiredMixin, ListView):
    model = MyModel
    template_name = 'app/mymodel_list.html'
    context_object_name = 'objects'
    paginate_by = 20
    login_url = reverse_lazy("login")

    def get_queryset(self):
        # Custom filtering
        return super().get_queryset()
```

## Code Style
- Usar nombres descriptivos de clase terminando en View (ej: OrderListView)
- Preferir override de métodos como get_queryset(), get_context_data() para customización
- Importar siempre LoginRequiredMixin cuando se requiera autenticación

## Models
- Usar TimeStampedModel como base cuando sea apropiado
- Definir __str__ para representación legible
- Usar verbose_name y verbose_name_plural
- Constantes de choices en inglés (nombre y valor en DB)
- Labels de choices en español

## Apps
- No crear archivo admin.py a menos que se solicite explícitamente

## Lógica de Negocio
- **Evitar Django signals** a menos que se solicite explícitamente
- **Evitar override del método save()** en modelos
- **Preferir lógica explícita**: Llamar métodos/funciones específicas después de operaciones
- Ejemplo preferido:
  ```python
  # En la vista
  order.save()
  create_result_for_order(order)  # Llamada explícita
  ```
- Mantener la lógica de negocio en vistas, servicios o funciones helper
- La lógica debe ser clara y rastreable, no "mágica" u oculta
