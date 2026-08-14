import logo from '../../assets/logo.png'

export default function Logo({ size = 56, className = '' }) {
  return (
    <img
      src={logo}
      alt="QuranInBangla"
      width={size}
      height={size}
      className={className}
    />
  )
}
