from django.test import TestCase

# Create your tests here.


#  <div class="d-flex justify-content-end mt-4">
#             <nav aria-label="Pagination" class="pagination">
#                 <ul class="pagination">
#                     {% if page_obj.has_previous %}
#                         <li class="page-item">
#                             <a class="page-link" href="?page=1" aria-label="First">
#                                 <span aria-hidden="true">&laquo;&laquo;</span>
#                             </a>
#                         </li>
#                         <li class="page-item">
#                             <a class="page-link" href="?page={{ page_obj.previous_page_number }}" aria-label="Previous">
#                                 <span aria-hidden="true">&laquo;</span>
#                             </a>
#                         </li>
#                     {% endif %}
        
#                     <li class="page-item disabled">
#                         <span class="page-link fw-bold text-dark"> <!-- Added classes -->
#                             Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
#                         </span>
#                     </li>
        
#                     {% if page_obj.has_next %}
#                         <li class="page-item">
#                             <a class="page-link" href="?page={{ page_obj.next_page_number }}" aria-label="Next">
#                                 <span aria-hidden="true">&raquo;</span>
#                             </a>
#                         </li>
#                         <li class="page-item">
#                             <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}" aria-label="Last">
#                                 <span aria-hidden="true">&raquo;&raquo;</span>
#                             </a>
#                         </li>
#                     {% endif %}
#                 </ul>
#             </nav>
#         </div>