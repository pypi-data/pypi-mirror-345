#ifndef __RACFU_ERROR_H_
#define __RACFU_ERROR_H_

#include <exception>
#include <iostream>
#include <string>
#include <vector>

namespace RACFu {
class RACFuError : public std::exception {
 private:
  std::vector<std::string> errors_;

 public:
  explicit RACFuError(const std::vector<std::string>& errors);
  explicit RACFuError(const std::string& error);
  const std::vector<std::string>& getErrors() const;
};
}  // namespace RACFu

#endif
