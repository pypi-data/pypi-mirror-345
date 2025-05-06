
#ifndef METATOMIC_TORCH_EXPORT_H
#define METATOMIC_TORCH_EXPORT_H

#ifdef METATOMIC_TORCH_STATIC_DEFINE
#  define METATOMIC_TORCH_EXPORT
#  define METATOMIC_TORCH_NO_EXPORT
#else
#  ifndef METATOMIC_TORCH_EXPORT
#    ifdef metatomic_torch_EXPORTS
        /* We are building this library */
#      define METATOMIC_TORCH_EXPORT __declspec(dllexport)
#    else
        /* We are using this library */
#      define METATOMIC_TORCH_EXPORT __declspec(dllimport)
#    endif
#  endif

#  ifndef METATOMIC_TORCH_NO_EXPORT
#    define METATOMIC_TORCH_NO_EXPORT 
#  endif
#endif

#ifndef METATOMIC_TORCH_DEPRECATED
#  define METATOMIC_TORCH_DEPRECATED __declspec(deprecated)
#endif

#ifndef METATOMIC_TORCH_DEPRECATED_EXPORT
#  define METATOMIC_TORCH_DEPRECATED_EXPORT METATOMIC_TORCH_EXPORT METATOMIC_TORCH_DEPRECATED
#endif

#ifndef METATOMIC_TORCH_DEPRECATED_NO_EXPORT
#  define METATOMIC_TORCH_DEPRECATED_NO_EXPORT METATOMIC_TORCH_NO_EXPORT METATOMIC_TORCH_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef METATOMIC_TORCH_NO_DEPRECATED
#    define METATOMIC_TORCH_NO_DEPRECATED
#  endif
#endif

#endif /* METATOMIC_TORCH_EXPORT_H */
