using UnityEngine;

namespace ProjectPenguin.Presentation.World
{
    public sealed class ProductionIslandPenguinView : MonoBehaviour
    {
        public enum Activity { CarryWalk, WorkLoop, Idle, Cheer }
        [SerializeField] private Animator _animator;
        [SerializeField] private GameObject _carriedItem;

        public void Configure(Animator animator, GameObject carriedItem)
        {
            _animator = animator;
            _carriedItem = carriedItem;
        }

        public void SetActivity(Activity activity)
        {
            if (_animator != null) _animator.Play(activity.ToString(), 0, 0f);
            if (_carriedItem != null) _carriedItem.SetActive(activity == Activity.CarryWalk);
        }

        private void Update()
        {
            if (_animator == null || _carriedItem == null) return;
            var carrying = _animator.GetCurrentAnimatorStateInfo(0).IsName("CarryWalk");
            if (_carriedItem.activeSelf != carrying) _carriedItem.SetActive(carrying);
        }
    }
}
